import json
import requests

API_URL = 'https://api.stormpath.com/v1/'

class Session(requests.Session):
    def __init__(self, auth, *args, **kwargs):
        super(Session, self).__init__(*args, **kwargs)
        self.headers.update({
            'content-type': 'application/json'
        })
        self.auth = auth

class Resource(object):
    """
    Resource is a thin layer over requests library
    used by all Stormpath resources.

    """

    def __init__(self, session=None, auth=None, **kwargs):
        self._uid = None
        self._is_dirty = False
        self.fields = getattr(self, 'fields', [])
        self.related_fields = getattr(self, 'related_fields', [])

        if session:
            self._session = session
        elif auth:
            self._session = Session(auth=auth())

        self._data = kwargs.get('data', {})
        self._data.update({k: v
            for k,v in kwargs.items()
            if k in self.fields})

        self._related_data = kwargs.get('related_data', {})
        self._related_data.update({k: v
            for k,v in kwargs.items()
            if k in self.related_fields})

        if self._data:
            self.url = self._data.get('href')
            if self.url:
                return

        self.url = kwargs.get('url')
        if not self.url:
            id = kwargs.get('id')
            if id:
                path = '%s/%s' % (self.path, id)
                self.url = '%s%s' % (API_URL, path)

    def __repr__(self):
        try:
            return "%s: %s" % (self.__class__.__name__, str(self))
        except:
            return self.__class__.__name__

    def __str__(self):
        return self.url

    @property
    def href(self):
        if self.url:
            return self.url

        raise Exception('Resource not saved, href is not available.')

    @property
    def uid(self):
        if self.url:
            uid = self.url[self.url.rfind('/')+1:]
            return uid
        raise Exception('Resource not saved, unique identifier is not available.')

    def create(self):
        url = '%s%s' % (API_URL, self.path)
        resp = self._session.post(url, data=json.dumps(self._data))
        if resp.status_code not in (200, 201):
            raise Exception(resp.json())

        self._data = resp.json()

    def read(self):
        if self._data:
            return

        resp = self._session.get(self.url)
        if resp.status_code != 200:
            raise NotImplementedError

        self._data = resp.json()

    def update(self):
        data = {k: v for k,v in self._data.items() if k in self.fields}
        resp = self._session.post(self.url, data=json.dumps(data))
        if resp.status_code != 200:
            raise NotImplementedError

        self._data = resp.json()

    def delete(self):
        resp = self._session.delete(self.url)
        if resp.status_code != 204:
            raise Exception('Unknown exception, DELETE failed')

        self._data = None
        self._uid = None
        self.url = None

    def save(self):
        if not self._is_dirty:
            return # FIXME: return False or something related?

        if self.uid:
            self.update()
        else:
            self.create()

    def __dir__(self):
        return self.fields

    def __getattr__(self, name):
        data = self.__dict__.get('_data')
        fields = self.__dict__.get('fields', [])
        related_fields = self.__dict__.get('related_fields', [])

        if name in fields or name in related_fields:
            if not data and 'url' in self.__dict__:
                self.read()
                data = self.__dict__.get('_data')

            if data and name in data:
                return data[name]

        raise AttributeError

    def __setattr__(self, name, value):
        data = self.__dict__.get('_data')
        fields = self.__dict__.get('fields', [])
        related_fields = self.__dict__.get('related_fields', [])

        if name in fields or name in related_fields:
            if not data and 'url' in self.__dict__:
                self.read()
                data = self.__dict__.get('_data')

        if data and name in fields:
            data[name] = value
            object.__setattr__(self, '_is_dirty', True)
        else:
            object.__setattr__(self, name, value)

class ResourceList(object):
    def __init__(self, session=None, auth=None, resource=None, url=None, *args, **kwargs):
        self._session = session or Session(auth=auth())
        self._resource_class = resource
        self._url = url

        self._offset = 0
        self._limit = 25
        self._items = None
        self._custom_request = False

        super(ResourceList, self).__init__(*args, **kwargs)

    def get(self, url):
        resp = self._resource_class(session=self._session, url=url)
        return resp

    def create(self, *args, **kwargs):
        if len(args) == 1:
            data = args[0]
        else:
            data = kwargs.get('data') or kwargs
        r = self._resource_class(session=self._session, data=data)
        r.create()
        return r

    def offset(self, offset):
        self._offset = offset
        self._custom_request = True
        return self

    def limit(self, limit):
        self._limit = limit
        self._custom_request = True
        return self

    def order(self, order):
        self._order = order
        self._custom_request = True
        return self

    def search(self, *args, **kwargs):
        if len(args) == 1:
            self._query = args[0]

        D = {k: v for k,v in kwargs.items() if k in self._resource_class.fields}
        if D:
            self._attr_query = D

        self._custom_request = True
        return self

    def _params(self):
        params = {}
        if hasattr(self, "_query"):
            params['q'] = self._query

        if hasattr(self, "_attr_query"):
            for k,v in self._attr_query.items():
                params[k] = v

        if hasattr(self, "_limit"):
            params['limit'] = self._limit

        if hasattr(self, "_offset"):
            params['offset'] = self._offset

        if hasattr(self, "_order"):
            params['orderBy'] = self._order

        return params

    def _fetch_items(self):
        params = self._params()

        resp = self._session.get(self._url, params=params)
        if resp.status_code != 200:
            raise NotImplementedError

        items = []
        data = resp.json()
        for item in data['items']:
            m = self._resource_class(session=self._session, data=item)
            items.append(m)

        return items

    def _fetch_next_page(self):
        self._offset += self._limit
        return self._fetch_items()

    def __getitem__(self, key):
        resp = self._session.get(self._url, data=json.dumps({}))
        if resp.status_code != 200:
            raise NotImplementedError

        data = resp.json()
        item = data['items'][key]
        return self._resource_class(session=self._session, data=item)

    def __iter__(self):
        # FIXME: implement pagination and cache
        if not self._items:
            self._items = self._fetch_items()

        while self._items:
            yield self._items.pop(0)

            # if not self._items check next resource page/collection
            if len(self._items) == 0 and self._custom_request == False:
                self._items.extend(self._fetch_next_page())

        else:
            raise StopIteration

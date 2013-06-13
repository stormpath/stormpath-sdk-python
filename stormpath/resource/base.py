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

        self._data = kwargs.get('data')
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
        if resp.status_code != 201:
            raise NotImplementedError

        self._data = resp.json()

    def read(self):
        if self._data:
            return

        resp = self._session.get(self.url, data=json.dumps({}))
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
        pass

    def save(self):
        if not self._is_dirty:
            return # FIXME: return False or something related

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

        if data and name in fields:
            data[name] = value
            object.__setattr__(self, '_is_dirty', True)
        else:
            object.__setattr__(self, name, value)

class ResourceList(object):
    def __init__(self, session=None, auth=None, *args, **kwargs):
        if session:
            self._session = session
        elif auth:
            self._session = Session(auth=auth())

        self._resource_class = kwargs.pop('resource')
        self._url = kwargs.pop('url')
        self._items = None
        super(ResourceList, self).__init__(*args, **kwargs)

    def get(self, url):
        resp = self._resource_class(session=self._session, url=url)
        return resp

    def create(self, data):
        r = self._resource_class(session=self._session, data=data)
        r.create()

    def __getitem__(self, key):
        resp = self._session.get(self._url, data=json.dumps({}))
        if resp.status_code != 200:
            raise NotImplementedError

        data = resp.json()
        item = data['items'][key]
        return self._resource_class(session=self._session, data=item)

    def __iter__(self):
        # fixme: implement pagination and cache
        if not self._items:
            resp = self._session.get(self._url, data=json.dumps({}))
            if resp.status_code != 200:
                raise NotImplementedError

            self._items = []
            data = resp.json()
            for item in data['items']:
                m = self._resource_class(session=self._session, data=item)
                self._items.append(m)
            self._items = self._items
        while self._items:
            yield self._items.pop(0)
            # if not self._items check next resource page/collection
        else:
            raise StopIteration

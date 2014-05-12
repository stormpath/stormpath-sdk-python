"""
Contains classes that bear the brunt of Stormpath Python SDK resource handling
like list access, updates, saves, deletes, attribute fetching, iterations etc.
"""


try:
    string_type = basestring
except NameError:
    string_type = str


class Expansion(object):
    """Handles resource expansions.

    More info in documentation:
    http://docs.stormpath.com/rest/product-guide/#links-expansion
    """

    def __init__(self, *args):
        self.items = {k: {} for k in args}

    def add_property(self, attr, offset=None, limit=None):
        d = {}

        if offset is not None:
            d['offset'] = offset

        if limit is not None:
            d['limit'] = limit

        self.items[attr] = d
        return self

    def get_params(self):
        ret = []

        for k, v in self.items.items():
            v = ','.join('%s:%d' % i for i in v.items())
            if v:
                v = '(' + v + ')'

            ret.append(k + v)

        return ','.join(ret)


class Resource(object):
    """Base class for all Stormpath resource objects.

    More information on what a resource object represents can be found in
    documentation:
    http://docs.stormpath.com/python/product-guide/#high-level-overview

    Most of the methods contained within this class are internal SDK methods.
    """
    autosaves = ()
    writable_attrs = ()

    def __init__(self, client, href=None, properties=None, query=None,
            expand=None):
        self._client = client
        self._expand = expand
        self._is_materialized = False
        self._query = query
        self._store = client.data_store

        if href is not None:
            if not isinstance(href, string_type):
                raise TypeError("'href' must be a string type")

            self._set_properties({'href': href})
        elif properties is not None:
            self._set_properties(properties)
        else:
            raise ValueError("%s: either 'href' or 'properties' are required",
                self._resource_class__.__name__)

    def __setattr__(self, name, value):
        if name.startswith('_') or name in self.writable_attrs:
            super(Resource, self).__setattr__(name, value)
        else:
            raise AttributeError("Attribute '%s' of %s is not writable" %
                (name, self.__class__.__name__))

    def __getattr__(self, name):
        if name == 'href':
            return self.__dict__.get('href')

        # If we already have it locally, no need to materialize the rest of
        # the resource.
        if name in self.__dict__:
            return self.__dict__[name]

        self._ensure_data()

        if name in self.__dict__:
            return self.__dict__[name]
        else:
            raise AttributeError("%s has no attribute '%s'" %
                (self.__class__.__name__, name))

    def get_resource_attributes(self):
        return {}

    def _wrap_resource_attr(self, cls, value):
        if isinstance(value, Resource):
            return value
        elif isinstance(value, dict):
            return cls(self._client, properties=value)
        elif value is None:
            return None
        else:
            raise TypeError("Can't convert '%s' to '%s'" %
                (type(value), cls.__name__))

    @staticmethod
    def _sanitize_property(value):
        if isinstance(value, Resource):
            if value.href:
                return {'href': value.href}
            else:
                return value._get_properties()
        elif isinstance(value, dict):
            return {Resource.to_camel_case(k):Resource._sanitize_property(v)
                for k, v in value.items()}
        else:
            return value

    def _set_properties(self, properties):
        resource_attrs = self.get_resource_attributes()
        for name, value in properties.items():
            name = self.from_camel_case(name)

            if name in resource_attrs:
                value = self._wrap_resource_attr(resource_attrs[name],
                    value)
            elif isinstance(value, dict) and 'href' in value:
                # No idea what kind of resource it is, but let's load it
                # it anyways.
                value = Resource(self._client, href=value['href'])

            self.__dict__[name] = value

        # If there were more properties than just the href, the resource is
        # materialized.
        if list(properties.keys()) != ['href']:
            self._is_materialized = True

    @staticmethod
    def to_camel_case(name):
        if '_' not in name:
            return name

        head, tail = name.split('_', 1)
        tail = tail.title().replace('_', '')

        return head + tail

    @staticmethod
    def from_camel_case(name):
        cs = []
        for c in name:
            cl = c.lower()
            if c == cl:
                cs.append(c)
            else:
                cs.append('_')
                cs.append(c.lower())

        return ''.join(cs)

    def _get_properties(self):
        data = {}
        for k, v in self.__dict__.items():
            if k in self.writable_attrs:
                data[self.to_camel_case(k)] = self._sanitize_property(v)

        return data

    def _get_property_names(self):
        return [a for a in self.__dict__.keys() if not a.startswith('_')]

    def __dir__(self):
        self._ensure_data()
        return self._get_property_names()

    def __repr__(self):
        return '<%s href=%s>' % (self.__class__.__name__, self.href)

    def __str__(self):
        try:
            return self.name
        except AttributeError:
            return repr(self)

    def is_materialized(self):
        return self._is_materialized

    def is_new(self):
        return self.href is None

    def _ensure_data(self):
        if self.is_new() or self.is_materialized():
            return

        params = {}
        if self._query:
            params.update(self._query)

        if self._expand:
            params.update({'expand': self._expand.get_params()})

        if not params:
            params = None

        data = self._store.get_resource(self.href, params=params)
        self._set_properties(data)


class SaveMixin(object):

    def save(self):
        if self.is_new():
            raise ValueError("Can't save new resources, use create instead")

        self._store.update_resource(self.href, self._get_properties())


class AutoSaveMixin(SaveMixin):

    def save(self):
        super(AutoSaveMixin, self).save()
        if self.is_materialized():
            for res in self.autosaves:
                self.__dict__[res].save()


class DeleteMixin(object):

    def delete(self):
        if self.is_new():
            return

        self._store.delete_resource(self.href)


class StatusMixin(object):
    """Provides a consistent resource status."""
    STATUS_ENABLED = 'ENABLED'
    STATUS_DISABLED = 'DISABLED'

    def get_status(self):
        self._ensure_data()
        return self.__dict__.get('status', self.STATUS_DISABLED).upper()

    def is_enabled(self):
        return self.get_status() == self.STATUS_ENABLED

    def is_disabled(self):
        return self.get_status() == self.STATUS_DISABLED


class DictMixin(object):
    """Provides dict() protocol support for the resource."""

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        return setattr(self, key, value)

    def __contains__(self, key):
        return hasattr(self, key)

    def keys(self):
        return [k for k in self.__dict__.keys() if not k.startswith('_')]

    def values(self):
        return [self.__dict__[k] for k in self.keys()]

    def items(self):
        return [(k, self.__dict__[k]) for k in self.keys()]

    def __iter__(self):
        return iter(self.keys())


class CollectionResource(Resource):
    """Provides Resource collections/lists.

    Every resource can be represented as part of a collection. We need to
    provide mechanisms for iterations and searches and support for offsets and
    limits when accessing a collection of data to avoid large data transfers
    when possible.

    More info on the logic of collections in documentation:
    http://docs.stormpath.com/rest/product-guide/#search
    """
    create_path = None
    readonly_attrs = ('href', 'items', 'limit', 'offset')
    resource_class = Resource

    def _set_properties(self, properties):
        items = properties.pop('items', None)
        super(CollectionResource, self)._set_properties(properties)

        if items is not None:
            self._is_materialized = True
            self.__dict__['items'] = [self._wrap_resource_attr(
                self.resource_class, item) for item in items]

    def _get_next_page(self, offset, limit):
        q = self._query or {}

        # If the user explicitly asked for a limited set of data, do nothing.
        if 'offset' in q or 'limit' in q:
            return []

        q['offset'] = offset
        q['limit'] = limit

        data = self._store.get_resource(self.href, params=q)

        items = [self._wrap_resource_attr(self.resource_class,
            item) for item in data['items']]
        self.__dict__['items'].extend(items)
        self.__dict__['limit'] += len(items)

        return items

    def __iter__(self):
        self._ensure_data()

        items = self.__dict__['items']
        offset = self.__dict__['offset']
        limit = self.__dict__['limit']

        while len(items) > 0:
            for item in items:
                yield item

            if len(items) < limit:
                break

            offset += len(items)
            items = self._get_next_page(offset, limit)

        # Update self._query so no more pagination is attempted.
        if self._query is None:
            self._query = {}

        self._query['offset'] = self.__dict__['offset']
        self._query['limit'] = self.__dict__['limit']

    def __len__(self):
        self._ensure_data()
        return len(self.__dict__['items'])

    def __getitem__(self, idx):
        if isinstance(idx, slice):
            start = idx.start or 0
            stop = idx.stop or 0

            query = {'offset': start}
            if stop and stop > start:
                query['limit'] = stop - start

            return self.query(**query)

        elif isinstance(idx, string_type):
            return self.get(idx)

        self._ensure_data()
        return self.__dict__['items'][idx]

    def get(self, href, expand=None):
        if '/' not in href:
            href = self._get_create_path() + '/' + href

        return self.resource_class(self._client, href=href,
            expand=expand)

    def search(self, query):
        if isinstance(query, dict):
            return self.query(**query)

        return self.query(q=query)

    def order(self, order_by):
        return self.query(orderBy=self.to_camel_case(order_by))

    def query(self, **kwargs):
        q = self._query or {}
        q.update(kwargs)
        q = {self.to_camel_case(k): v for k, v in q.items()}

        return self.__class__(self._client, self.href, query=q)

    def _get_create_path(self):
        if self.create_path:
            return self._client.BASE_URL + self.create_path
        elif self.href.startswith(self._client.BASE_URL):
            return self.href
        else:
            return self._client.BASE_URL + self.href

    def create(self, properties, expand=None, **params):
        data = {}
        for k, v in properties.items():
            if k in self.resource_class.writable_attrs:
                data[self.to_camel_case(k)] = self._sanitize_property(v)

        params = {self.to_camel_case(k): v for k, v in params.items()}
        if expand:
            params.update({'expand': expand.get_params()})

        return self.resource_class(
            self._client,
            properties = self._store.create_resource(
                self._get_create_path(),
                data,
                params = params
            )
        )

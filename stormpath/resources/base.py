"""
Contains classes that bear the brunt of Stormpath Python SDK resource handling
like list access, updates, saves, deletes, attribute fetching, iterations etc.
"""

import datetime
from copy import deepcopy
from dateutil.parser import parse
from isodate import duration_isoformat, parse_duration
from json import JSONEncoder, dumps

try:
    string_type = basestring
except NameError:
    string_type = str

from pydispatch import dispatcher


SIGNAL_RESOURCE_CREATED = 'resource-created'
SIGNAL_RESOURCE_UPDATED = 'resource-updated'
SIGNAL_RESOURCE_DELETED = 'resource-deleted'


class ResourceEncoder(JSONEncoder):
    def default(self, o):
        data = {}

        if isinstance(o, Resource):
            resource_attrs = o._get_property_names()
            expand_attrs = o._expand.items.keys() if o._expand else []

            for attr in resource_attrs:
                value = o.__dict__.get(o.from_camel_case(attr))
                if isinstance(value, Resource):
                    if attr in map(o.from_camel_case, expand_attrs):
                        sub_resource = self.default(value)
                        if sub_resource:
                            data[attr] = sub_resource
                    else:
                        data[attr] = {'href': value.href}
                elif isinstance(value, datetime.datetime):
                    data[attr] = value.isoformat()
                else:
                    data[attr] = value

        return data


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
    resolvable_attrs = ()
    timedelta_attrs = ()

    def __init__(self, client, href=None, properties=None, query=None, expand=None):
        self._client = client
        self._expand = expand
        self._query = query
        self._store = client.data_store

        if href is not None:
            if not isinstance(href, string_type):
                raise TypeError("'href' must be a string type")

            self._set_properties({'href': href})
        elif properties is not None:
            self._set_properties(properties)
        else:
            raise ValueError("Either 'href' or 'properties' are required")

    def __setattr__(self, name, value):
        ctype = self.get_resource_attributes().get(name)

        if ctype and not isinstance(value, ctype) and name in self.writable_attrs:
            getattr(self, name)._set_properties(value)
        elif name.startswith('_') or name in self.writable_attrs:
            super(Resource, self).__setattr__(name, value)
        else:
            raise AttributeError("Attribute '%s' of %s is not writable" % (name, self.__class__.__name__))

    def __getattr__(self, name):
        if name == 'href':
            return self.__dict__.get('href')

        self._ensure_data()

        if name in self.__dict__:
            return self.__dict__[name]
        else:
            raise AttributeError("%s has no attribute '%s'" % (self.__class__.__name__, name))

    @staticmethod
    def get_resource_attributes():
        return {}

    def _wrap_resource_attr(self, cls, value):
        if isinstance(value, Resource):
            return value
        elif isinstance(value, dict) or (isinstance(value, list) and cls == ListOnResource):
            return cls(self._client, properties=value)
        elif value is None:
            return None
        else:
            raise TypeError("Can't convert '%s' to '%s'" % (type(value), cls.__name__))

    @staticmethod
    def _sanitize_property(value):
        if isinstance(value, Resource):
            if value.href:
                return {'href': value.href}
            else:
                return value._get_properties()
        elif isinstance(value, dict):
            return {Resource.to_camel_case(k): Resource._sanitize_property(v)
                for k, v in value.items()}
        elif isinstance(value, FixedAttrsDict):
            return value._get_properties()
        else:
            return value

    def _set_properties(self, properties, overwrite=False):
        resource_attrs = self.get_resource_attributes()

        for name, value in properties.items():
            name = self.from_camel_case(name)

            # if this attribute is already set, don't overwrite it
            if not overwrite:
                if name in self.writable_attrs and name in self.__dict__:
                    continue

            if name in resource_attrs:
                value = self._wrap_resource_attr(resource_attrs[name], value)
                if hasattr(resource_attrs[name], '_set_parent_and_name'):
                    value._set_parent_and_name(self, name)
            elif isinstance(value, dict) and 'href' in value:
                # No idea what kind of resource it is, but let's load it
                # it anyways.
                value = Resource(self._client, href=value['href'])
            elif name in ['created_at', 'modified_at']:
                value = parse(value)
            elif name in self.timedelta_attrs:
                value = parse_duration(value)

            self.__dict__[name] = value

    @staticmethod
    def to_camel_case(name):
        if '_' not in name:
            return name

        head, tail = name.split('_', 1)
        tail = tail.title().replace('_', '')

        return head + tail

    @staticmethod
    def from_camel_case(name):
        if 'oauthpolicy' == name.lower():
            return 'oauth_policy'

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
                if k in self.timedelta_attrs and isinstance(v, datetime.timedelta):
                    v = duration_isoformat(v)

                data[self.to_camel_case(k)] = self._sanitize_property(v)

        return data

    def resolve_object(self, reference, cls):
        cls_name = cls.__name__.lower() + 's'

        if isinstance(reference, str) and reference.startswith(self._client.BASE_URL):
            return getattr(self._client, cls_name).get(reference)

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

    def is_new(self):
        return self.href is None

    def _ensure_data(self, overwrite=False):
        if self.is_new():
            return

        params = {}
        if self._query:
            params.update(self._query)

        if self._expand:
            params.update({'expand': self._expand.get_params()})

        if 'limit' in self.__dict__ and 'offset' in self.__dict__:
            params['limit'] = self.__dict__['limit']
            params['offset'] = self.__dict__['offset']

        if not params:
            params = None

        data = self._store.get_resource(self.href, params=params)
        self._set_properties(data, overwrite=overwrite)

    def refresh(self):
        """Refreshes the local copy of a Resource or Resource List from the API

        Example refreshing an application list after delete::

            myapp = client.applications[0]
            myapp.delete()

            client.applications.refresh()

        .. note::
            This will ignore all changes made on a resource if it has not been saved previously.
        """
        self._store.uncache_resource(self.href)
        self._ensure_data(True)

    def to_json(self):
        return dumps(self, cls=ResourceEncoder)


class SaveMixin(object):
    def save(self):
        if self.is_new():
            raise ValueError("Can't save new resources, use create instead")

        properties = self._get_properties()
        data = self._store.update_resource(self.href, properties)

        dispatcher.send(signal=SIGNAL_RESOURCE_UPDATED, sender=self, href=self.href, properties=properties)

        if hasattr(self, 'modified_at') and 'modifiedAt' in data:
            self.__dict__['modified_at'] = parse(data.get('modifiedAt'))


class AutoSaveMixin(SaveMixin):
    def save(self):
        super(AutoSaveMixin, self).save()

        for res in self.autosaves:
            if res in self.__dict__:
                self.__dict__[res].save()


class DeleteMixin(object):

    def delete(self):
        if self.is_new():
            return

        self._store.delete_resource(self.href)
        dispatcher.send(signal=SIGNAL_RESOURCE_DELETED, sender=self, href=self.href)


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
        self._ensure_data()
        return [k for k in self.__dict__.keys() if not k.startswith('_')]

    def values(self):
        return [self.__dict__[k] for k in self.keys()]

    def items(self):
        return [(k, self.__dict__[k]) for k in self.keys()]

    def __iter__(self):
        return iter(self.keys())

    def update(self, dct):
        for k, v in dct.items():
            setattr(self, k, v)

        if isinstance(self, SaveMixin):
            self.save()


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
    readonly_attrs = ('href', 'items', 'limit', 'offset', 'size')
    resource_class = Resource

    def _set_properties(self, properties, overwrite=False):
        props = properties.copy()
        items = props.pop('items', None)

        super(CollectionResource, self)._set_properties(props, overwrite=overwrite)

        if items is not None:
            self.__dict__['items'] = [self._wrap_resource_attr(self.resource_class, item) for item in items]

    def _get_next_page(self, offset, limit):
        params = deepcopy(self._query) or {}

        # If the user explicitly asked for a limited set of data, do nothing.
        if 'offset' in params or 'limit' in params:
            return []

        # We know the full size of the Collection via the size property
        # we get from the API. If we've reached the end don't make
        # that one extra API call because it's not necessary
        if not (offset < self.size):
            return []

        params['offset'] = offset
        params['limit'] = limit

        data = self._store.get_resource(self.href, params=params)
        items = [self._wrap_resource_attr(self.resource_class, item) for item in data.get('items', [])]
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

            # don't attempt to do another page as we've fetched all items
            if len(items) < limit:
                break

            offset += len(items)
            items = self._get_next_page(offset, limit)

        self.__dict__['limit'] = limit

    def __len__(self):
        self._ensure_data()
        return self.__dict__.get('_sliced_size', self.size)

    def __getitem__(self, idx):
        if isinstance(idx, slice):
            start = idx.start or 0
            stop = idx.stop or 0

            query = {'offset': start}
            if stop and stop > start:
                query['limit'] = stop - start

            r = self.query(**query)
            # We need to make sure we either report the total size of the collection
            # or the sliced size if we used. for example, coll[2:8]
            r.__dict__['_sliced_size'] = min(query.get('limit', r.size), max(0, r.size - query['offset']))

            return r

        elif isinstance(idx, string_type):
            return self.get(idx)

        self._ensure_data()

        return self.__dict__['items'][idx]

    def get(self, href, expand=None):
        if '/' not in href:
            href = self._get_create_path() + '/' + href

        return self.resource_class(self._client, href=href, expand=expand)

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

    def _prepare_for_create(self, properties, expand=None, **params):
        resource_attrs = self.resource_class.get_resource_attributes()
        data = {}

        for k, v in properties.items():
            if isinstance(v, dict) and k in resource_attrs:
                v = self._wrap_resource_attr(resource_attrs[k], v)

            if k in self.resource_class.writable_attrs:
                data[self.to_camel_case(k)] = self._sanitize_property(v)

        params = {self.to_camel_case(k): v for k, v in params.items()}
        if expand:
            params.update({'expand': expand.get_params()})

        return data, params

    def create(self, properties, expand=None, **params):
        data, params = self._prepare_for_create(properties, expand, **params)

        created = self.resource_class(self._client, properties=self._store.create_resource(self._get_create_path(), data, params=params))
        dispatcher.send(signal=SIGNAL_RESOURCE_CREATED, sender=self.resource_class, data=data, params=params)

        return created


class FixedAttrsDict(DictMixin):
    """
    Dict with fixed attribute list.
    """
    writable_attrs = ()

    @staticmethod
    def get_dict_attributes():
        return {}

    def __init__(self, client, properties):
        self._set_properties(properties)

    def __setattr__(self, name, value):
        if name.startswith('_') or name in self.writable_attrs:
            super(FixedAttrsDict, self).__setattr__(name, value)
        else:
            raise AttributeError("Attribute '%s' of %s is not writable" % (name, self.__class__.__name__))

    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]
        else:
            raise AttributeError("%s has no attribute '%s'" % (self.__class__.__name__, name))

    def __dir__(self):
        return self.__dict__.keys()

    def keys(self):
        return [k for k in self.__dict__.keys() if not k.startswith('_')]

    def _wrap_resource_attr(self, cls, value):
        if isinstance(value, FixedAttrsDict):
            return value
        elif isinstance(value, dict):
            return cls(None, properties=value)
        elif value is None:
            return None
        else:
            raise TypeError("Can't convert '%s' to '%s'" % (type(value), cls.__name__))

    def _set_properties(self, properties, overwrite=False):
        resource_attrs = self.get_dict_attributes()
        for name, value in properties.items():
            name = Resource.from_camel_case(name)

            if name in resource_attrs:
                value = self._wrap_resource_attr(resource_attrs[name], value)

            self.__dict__[name] = value

    def _get_properties(self):
        data = {}
        for k, v in self.__dict__.items():
            if k in self.writable_attrs:
                data[Resource.to_camel_case(k)] = self._sanitize_property(v)

        return data

    @staticmethod
    def _sanitize_property(value):
        if isinstance(value, dict):
            return {Resource.to_camel_case(k): Resource._sanitize_property(v) for k, v in value.items()}
        elif isinstance(value, FixedAttrsDict):
            return value._get_properties()
        else:
            return value

    @staticmethod
    def get_resource_attributes():
        return {}


class ListOnResource(list):
    """
    List on resource that refreshes on append.
    """
    parent_resource = None
    list_name = None
    type = None

    def __init__(self, client, properties, type=None):
        self.type = type

        if self.type:
            properties = [self.type(**el) for el in properties]

        super(ListOnResource, self).__init__(properties)

    def _set_properties(self, properties):
        super(ListOnResource, self).__init__(properties)

    def _get_properties(self):
        if self.type:
            return [{
                Resource.to_camel_case(k): self.type._sanitize_property(v)
                for k, v in el.items() if k in self.type.writable_attrs
            } for el in self]
        else:
            return self

    def _set_parent_and_name(self, parent, name):
        self.parent_resource = parent
        self.list_name = name

    def append(self, p_object):
        self.parent_resource.refresh()
        self._set_properties(getattr(self.parent_resource, self.list_name))
        super(ListOnResource, self).append(p_object)

        setattr(self.parent_resource, self.list_name, self)

    def extend(self, list):
        self.parent_resource.refresh()
        self._set_properties(getattr(self.parent_resource, self.list_name))
        super(ListOnResource, self).extend(list)

        setattr(self.parent_resource, self.list_name, self)

    def insert(self, index, object):
        self.parent_resource.refresh()
        self._set_properties(getattr(self.parent_resource, self.list_name))
        super(ListOnResource, self).insert(index, object)

        setattr(self.parent_resource, self.list_name, self)

    def pop(self, index=None):
        if index is None:
            index = -1

        value = self[index]

        self.parent_resource.refresh()
        self._set_properties(getattr(self.parent_resource, self.list_name))

        if value in self:
            super(ListOnResource, self).remove(value)

        setattr(self.parent_resource, self.list_name, self)

        return value

    def remove(self, value):
        had_value = value in self

        self.parent_resource.refresh()
        self._set_properties(getattr(self.parent_resource, self.list_name))
        try:
            super(ListOnResource, self).remove(value)
        except ValueError as e:
            if had_value:
                pass
            else:
                raise e

        setattr(self.parent_resource, self.list_name, self)

    def __delitem__(self, key):
        value = self[key]

        self.parent_resource.refresh()
        self._set_properties(getattr(self.parent_resource, self.list_name))

        if value in self:
            super(ListOnResource, self).remove(value)

        setattr(self.parent_resource, self.list_name, self)

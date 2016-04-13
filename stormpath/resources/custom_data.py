"""Stormpath CustomData resource mappings."""

from dateutil.parser import parse

from .base import (
    DeleteMixin,
    Resource,
    SaveMixin,
)


class CustomData(Resource, DeleteMixin, SaveMixin):
    """CustomData Resource for custom user data.

    Resources have predefined fields that are useful to many applications,
    but you are likely to have your own custom data that you need to associate
    with a resource as well. It behaves like a Python dictionary.

    More info in documentation:
    http://docs.stormpath.com/rest/product-guide/#custom-data
    """
    data_field = '_data'
    readonly_attrs = (
        'created_at',
        'href',
        'ionmeta',
        'ion_meta',
        'meta',
        'modified_at',
        'spmeta',
        'sp_meta',
        'sp_http_status',
    )

    exposed_readonly_timestamp_attrs = (
        'created_at',
        'modified_at',
    )

    def __init__(self, *args, **kwargs):
        super(CustomData, self).__init__(*args, **kwargs)
        self._deletes = set([])

    def __getitem__(self, key):
        if key == self.data_field:
            return self.__dict__[self.data_field]

        if (key not in self.__dict__.get(self.data_field, {})) and \
                (self._get_key_href(key) not in self._deletes):
            self._ensure_data()

        return getattr(self, self.data_field)[key]

    def __setitem__(self, key, value):
        if key == self.data_field:
            self.__dict__[self.data_field] = value

        if key in self.readonly_attrs or \
                self.from_camel_case(key) in self.readonly_attrs:
            raise KeyError(
                "Custom data property '%s' is not writable" % (key))
        else:
            if key.startswith('-'):
                raise KeyError(
                    "Usage of '-' at the beginning of key is not allowed")

            key_href = self._get_key_href(key)
            if key_href in self._deletes:
                self._deletes.remove(key_href)

            getattr(self, self.data_field)[key] = value

    def __delitem__(self, key):
        if key in self.exposed_readonly_timestamp_attrs:
            raise KeyError(
                "Custom data property '%s' is not deletable" % (key))

        self._ensure_data()

        for href in self._deletes:
            try:
                del self.__dict__.get(self.data_field, {})[href.split('/')[-1]]
            except KeyError:
                pass

        del self.__dict__.get(self.data_field, {})[key]

        if not self.is_new():
            self._deletes.add(self._get_key_href(key))

    def __contains__(self, key):
        self._ensure_data()
        return key in self.__dict__.get(self.data_field, {})

    def __setattr__(self, name, value):
        ctype = self.get_resource_attributes().get(name)

        if ctype and not isinstance(value, ctype) \
                and name not in self.readonly_attrs:
            getattr(self, name)._set_properties(value)
        elif name.startswith('_') or name in self.writable_attrs:
            super(CustomData, self).__setattr__(name, value)
        else:
            self._set_properties({name: value})

    def __getattr__(self, name):
        if name == 'href':
            return self.__dict__.get('href')

        self._ensure_data()
        if name in self.__dict__:
            return self.__dict__[name]
        elif name in self.__dict__[self.data_field]:
            return self.__dict__[self.data_field][name]
        else:
            raise AttributeError(
                "%s has no attribute '%s'" %
                (self.__class__.__name__, name))

    def _get_key_href(self, key):
        return '%s/%s' % (self.href, key)

    def keys(self):
        self._ensure_data()
        return self.__dict__.get(self.data_field, {}).keys()

    def values(self):
        self._ensure_data()
        return self.__dict__.get(self.data_field, {}).values()

    def items(self):
        self._ensure_data()
        return self.__dict__.get(self.data_field, {}).items()

    def get(self, key, default=None):
        try:
            return self.__getitem__(key)
        except KeyError:
            return default

    def __iter__(self):
        self._ensure_data()
        return iter(self.__dict__.get(self.data_field, {}))

    def _get_properties(self):
        data = self.__dict__.get(self.data_field, {})
        writable_attrs = set(data) - set(
            self.exposed_readonly_timestamp_attrs)
        if data:
            return {k: self.__dict__[self.data_field][k] for k in writable_attrs}
        return data

    def _set_properties(self, properties, overwrite=False):
        data = self.__dict__.get(self.data_field, {})
        for k, v in properties.items():
            kcc = self.from_camel_case(k)
            if kcc in self.readonly_attrs:
                if kcc in self.exposed_readonly_timestamp_attrs:
                    v = parse(v)
                    data[kcc] = v
                self.__dict__[kcc] = v
            else:
                if k not in data:
                    data[k] = v
        if data:
            self.__dict__[self.data_field] = data

    def save(self):
        for href in self._deletes:
            self._store.delete_resource(href)

        self._deletes = set()

        if self.data_field in self.__dict__ and \
                len(self._get_properties()):
            super(CustomData, self).save()

    def delete(self):
        super(CustomData, self).delete()
        self.__dict__[self.data_field] = {}

"""Stormpath CustomData resource mappings."""


from .base import (
    DeleteMixin,
    Resource,
    SaveMixin,
)


class CustomData(DeleteMixin, Resource, SaveMixin):
    """CustomData Resource for custom user data.

    Resources have predefined fields that are useful to many applications,
    but you are likely to have your own custom data that you need to associate
    with a resource as well. It behaves like a Python dictionary.

    More info in documentation:
    http://docs.stormpath.com/rest/product-guide/#custom-data

    """
    readonly_attrs = (
        'href', 'created_at', 'modified_at', 'meta', 'sp_meta', 'spmeta',
        'ionmeta', 'ion_meta')

    def __getitem__(self, key):
        if key not in self.data:
            self._ensure_data()

        return self.data[key]

    def __setitem__(self, key, value):
        if key in self.readonly_attrs or \
                self.from_camel_case(key) in self.readonly_attrs:
            raise KeyError(
                "Custom data property '%s' is not writable" % (key))
        else:
            if key.startswith('-'):
                raise KeyError(
                    "Usage of '-' at the beggining of key is not allowed")

            key_href = self._get_key_href(key)
            if key_href in self._deletes:
                self._deletes.remove(key_href)
            self.data[key] = value

    def __delitem__(self, key):
        self._ensure_data()

        del self.data[key]
        if not self.is_new():
            self._deletes.add(self._get_key_href(key))

    def __contains__(self, key):
        return key in self.data

    def _get_key_href(self, key):
        return '%s/%s' % (self.href, key)

    def save(self):
        if 'data' in self.__dict__ and len(self.data):
            super(CustomData, self).save()

    def keys(self):
        return self.data.keys()

    def values(self):
        return self.data.values()

    def items(self):
        return self.data.items()

    def get(self, key, default=None):
        try:
            return self.__getitem__(key)
        except KeyError:
            return default

    def __iter__(self):
        return iter(self.data)

    def _get_properties(self):
        return dict((k, self._sanitize_property(v)) for k, v in self.items())

    def _set_properties(self, properties):
        self.__dict__['data'] = self.__dict__.get('data', {})
        for k, v in properties.items():
            kcc = self.from_camel_case(k)
            if kcc in self.readonly_attrs:
                self.__dict__[kcc] = v
            else:
                if k not in self.__dict__['data']:
                    self.__dict__['data'][k] = v
        self._is_materialized = ('created_at' in self.__dict__)

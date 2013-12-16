from .base import Resource, SaveMixin, DeleteMixin


class CustomData(Resource, SaveMixin, DeleteMixin):

    readonly_attrs = (
        'href', 'created_at', 'modified_at', 'meta', 'sp_meta', 'spmeta',
        'ionmeta', 'ion_meta')

    def __getitem__(self, key):
        if key not in self.data:
            self._ensure_data()

        return self.data[key]

    def __setitem__(self, key, value):
        if key in self.readonly_attrs:
            raise KeyError(
                "Custom data property '%s' is not writable" % (key))
        else:
            if '%s/%s' % (self.href, key) in self._deletes:
                self._deletes.remove('%s/%s' % (self.href, key))
            self.data[key] = value

    def __delitem__(self, key):
        if key in self.data:
            del self.data[key]

        if not self.is_new():
            self._deletes.add('%s/%s' % (self.href, key))

    def __contains__(self, key):
        return key in self.data

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

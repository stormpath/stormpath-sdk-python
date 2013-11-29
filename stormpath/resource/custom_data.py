from .base import Resource, SaveMixin, DeleteMixin, string_type


class CustomData(Resource, SaveMixin, DeleteMixin):

    readonly_attrs = (
        'href', 'created_at', 'modified_at', 'meta', 'sp_meta', 'spmeta',
        'ionmeta', 'ion_meta')

    def __getitem__(self, key):
        if isinstance(key, string_type):
            if key not in self.__dict__.keys() and \
                    key not in self.__dict__['data'].keys():
                self._ensure_data()

            if key in self.readonly_attrs:
                return self.__dict__[key]
            else:
                return self.__dict__['data'][key]

    def __setitem__(self, key, value):
        if isinstance(key, string_type):
            if key in self.readonly_attrs:
                raise TypeError(
                    "Custom data property '%s' is not writable" % (key))
            else:
                self.__dict__['data'][key] = value
                print(self.__dict__['data'])
        else:
            raise TypeError("Key not a string")

    def is_materialized(self, attr=None):
        if len(self.data) > 1 and 'href' in self.data:
            return True
        return False

    def _get_properties(self):
        data = {}
        for k, v in self.__dict__['data'].items():
            if k not in self.readonly_attrs:
                data[k] = self._sanitize_property(v)
        return data

    def _set_properties(self, properties):
        self.__dict__['data'] = self.__dict__.get('data', {})
        for name, value in properties.items():
            if self.from_camel_case(name) in self.readonly_attrs:
                self.__dict__[self.from_camel_case(name)] = value
            else:
                self.__dict__['data'][name] = value

"""Stormpath Provider Data resource mappings."""


from dateutil.parser import parse

from .base import Resource, DictMixin


class ProviderData(Resource, DictMixin):
    """Stormpath Provider Data resource.

    More info in documentation:
    http://docs.stormpath.com/python/product-guide/#integrating-with-google
    http://docs.stormpath.com/python/product-guide/#integrating-with-facebook
    """

    writable_attrs = (
        'access_token',
        'code',
        'provider_id',
        'refresh_token',
    )

    exposed_readonly_timestamp_attrs = (
        'created_at',
        'modified_at',
    )

    def _set_properties(self, properties):
        super(ProviderData, self)._set_properties(properties)

        for attr in self.exposed_readonly_timestamp_attrs:
            value = self.__dict__.get(attr)
            if value:
                self.__dict__[attr] = parse(value)

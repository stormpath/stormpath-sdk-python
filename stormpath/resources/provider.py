"""Stormpath Provider resource mappings."""


from .base import (
    DeleteMixin,
    DictMixin,
    Resource,
    SaveMixin,
)


class Provider(Resource, DeleteMixin, DictMixin, SaveMixin):
    """Stormpath Provider resource.

    More info in documentation:
    http://docs.stormpath.com/python/product-guide/#integrating-with-google
    """

    GOOGLE = 'google'
    FACEBOOK = 'facebook'
    GITHUB = 'GITHUB'
    LINKEDIN = 'linkedin'
    STORMPATH = 'stormpath'

    writable_attrs = (
        'client_id',
        'client_secret',
        'redirect_uri',
        'provider_id',
    )

    def save(self):
        if self.provider_id == self.STORMPATH:
            return
        if self.is_new():
            raise ValueError("Can't save new resources, use create instead")

        self._store.update_resource(self.href, self._get_properties())


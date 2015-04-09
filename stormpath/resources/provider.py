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
    GITHUB = 'github'
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

        super(Provider, self).save()

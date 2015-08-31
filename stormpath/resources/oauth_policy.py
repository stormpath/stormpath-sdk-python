"""Stormpath oAuthPolicy resource mappings."""


from .base import (
    DictMixin,
    Resource,
    SaveMixin,
)


class OauthPolicy(Resource, DictMixin, SaveMixin):
    """Stormpath oAuthPolicy resource.

    More info in documentation:
    http://docs.stormpath.com/guides/token-management/
    """
    writable_attrs = (
        'access_token_ttl',
        'refresh_token_ttl',
    )

    timedelta_attrs = (
        'access_token_ttl',
        'refresh_token_ttl',
    )

    @staticmethod
    def get_resource_attributes():
        from .application import Application
        from .tenant import Tenant

        return {
            'application': Application,
            'tenant': Tenant,
        }

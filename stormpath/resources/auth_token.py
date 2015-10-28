"""Stormpath AccessToken resource mappings."""


from .base import (
    CollectionResource,
    DeleteMixin,
    DictMixin,
    Resource,
)


class AuthToken(Resource, DictMixin, DeleteMixin):
    """Authentication token resource."""

    @staticmethod
    def get_resource_attributes():
        from .account import Account
        from .application import Application
        from .tenant import Tenant

        return {
            'account': Account,
            'application': Application,
            'tenant': Tenant,
        }


class AuthTokenList(CollectionResource):
    """AuthToken resource list."""
    resource_class = AuthToken

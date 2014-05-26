"""Stormpath ApiKey resource mappings."""


from .base import (
    CollectionResource,
    DeleteMixin,
    Resource,
    SaveMixin,
    StatusMixin,
)


class ApiKey(Resource, DeleteMixin, SaveMixin, StatusMixin):
    writable_attrs = (
        'status',
    )

    @staticmethod
    def get_resource_attributes():
        from .account import Account
        from .tenant import Tenant

        return {
            'account': Account,
            'tenant': Tenant,
        }


class ApiKeyList(CollectionResource):
    """Application resource list."""
    create_path = '/apiKeys'
    resource_class = ApiKey

    def get_key(self, client_id):
        try:
            return self.search({'id': client_id})[0]
        except IndexError:
            return False


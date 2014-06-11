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
    resource_class = ApiKey

    def get_key(self, client_id):
        try:
            return self.search({'id': client_id})[0]
        except IndexError:
            return False

    def create(self, expand=None):
        resource_attrs = self.resource_class.get_resource_attributes()
        data = {}
        params = {}
        if expand:
            params.update({'expand': expand.get_params()})

        return self.resource_class(
            self._client,
            properties=self._store.create_resource(
                self._get_create_path(),
                data,
                params=params
            )
        )

"""Stormpath ApiKey resource mappings."""

from .base import (
    CollectionResource,
    DeleteMixin,
    DictMixin,
    Resource,
    SaveMixin,
    StatusMixin,
)
from stormpath.error import Error


class ApiKey(Resource, DictMixin, DeleteMixin, SaveMixin, StatusMixin):
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

    def _ensure_data(self):
        if self.href == '/apiKeys':
            raise ValueError(
                "It is not possible to access api_keys from the "
                "Client resource! Try using the Application resource instead.")

        super(ApiKeyList, self)._ensure_data()

    def get_key(self, client_id, client_secret=None):
        search = {'id': client_id}
        try:
            key = None

            # First, try to get the key from the cache using its ID.
            if '/applications' in self.href:
                href = '%s/apiKeys/%s' % (
                    self.href.split('/applications')[0], client_id)
                try:
                    key = self.resource_class(self._client, href)
                    key.secret
                except Error:
                    key = None

            # If there was no key with client_id in cache, make HTTP
            # request to the Stormpath service
            if not key:
                key = self.search(search)[0]

            if client_secret and not client_secret == key.secret:
                return False
            return key
        except IndexError:
            return False

    def create(self, expand=None):
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

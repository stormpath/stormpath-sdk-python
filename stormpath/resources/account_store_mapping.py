"""Stormpath AccountStoreMapping resource."""


from .base import (
    CollectionResource,
    DeleteMixin,
    DictMixin,
    Resource,
    SaveMixin,
)


class AccountStoreMapping(Resource, DeleteMixin, DictMixin, SaveMixin):
    """Mapping between an Application and an Account Store.

    Account Store is a generic term for a resource that stores Accounts.
    Currently, this includes Directories and Groups.

    More info in documentation:
    http://docs.stormpath.com/python/product-guide/#account-store-mappings
    """
    writable_attrs = (
        'account_store',
        'application',
        'is_default_account_store',
        'is_default_group_store',
        'list_index',
    )

    @staticmethod
    def get_resource_attributes():
        from .account_store import AccountStore
        from .application import Application

        return {
            'account_store': AccountStore,
            'application': Application,
        }


class AccountStoreMappingList(CollectionResource):
    """Account Store Mapping list."""

    create_path = '/accountStoreMappings'
    resource_class = AccountStoreMapping

    def _ensure_data(self):
        if self.href == '/accountStoreMappings':
            raise ValueError(
                "It is not possible to access account_store_mappings from "
                "Client resource! Try using Application resource instead.")

        super(AccountStoreMappingList, self)._ensure_data()

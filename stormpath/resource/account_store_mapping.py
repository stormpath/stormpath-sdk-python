from .base import Resource, ResourceList
from ..error import Error


class AccountStoreMapping(Resource):
    """Mapping between an Application and an account store.

    Account Store is a generic term for a resource that stores Accounts.
    Currently, this includes Directories and Groups.

    More info in documentation:
    https://www.stormpath.com/docs/python/product-guide#ManageAccountStores
    """

    writable_attrs = ('application', 'account_store', 'list_index',
        'is_default_account_store', 'is_default_group_store')

    def get_resource_attributes(self):
        from .application import Application
        from .account_store import AccountStore

        return {
            'application': Application,
            'account_store': AccountStore,
        }


class AccountStoreMappingList(ResourceList):
    """Account Store Mapping list."""

    create_path = '/accountStoreMappings'
    resource_class = AccountStoreMapping

"""Stormpath OrganizationAccountStoreMapping resource."""


from .base import (
    CollectionResource,
    DeleteMixin,
    DictMixin,
    Resource,
    SaveMixin,
)


class OrganizationAccountStoreMapping(Resource, DeleteMixin, DictMixin,
                                      SaveMixin):
    """Mapping between an Organization and an Account Store.

    Account Store is a generic term for a resource that stores Accounts.
    Currently, this includes Directories and Groups.

    More info in documentation:
    http://docs.stormpath.com/python/product-guide/#adding-an-account-store-to-an-organization
    """
    writable_attrs = (
        'account_store',
        'organization',
        'is_default_account_store',
        'is_default_group_store',
        'list_index',
    )

    @staticmethod
    def get_resource_attributes():
        from .account_store import AccountStore
        from .organization import Organization

        return {
            'account_store': AccountStore,
            'organization': Organization,
        }


class OrganizationAccountStoreMappingList(CollectionResource):
    """Organization Account Store Mapping list."""

    create_path = '/organizationAccountStoreMappings'
    resource_class = OrganizationAccountStoreMapping

    def _ensure_data(self):
        if self.href == '/organizationAccountStoreMappings':
            raise ValueError(
                "It is not possible to access "
                "organization_account_store_mappings from the Client "
                "resource! Try using the Organization resource instead.")

        super(OrganizationAccountStoreMappingList, self)._ensure_data()

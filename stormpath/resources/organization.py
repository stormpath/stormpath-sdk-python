"""Stormpath Organization resource mappings."""


from .base import (
    AutoSaveMixin,
    CollectionResource,
    DeleteMixin,
    DictMixin,
    Resource,
    StatusMixin,
)


class Organization(Resource, AutoSaveMixin, DeleteMixin, DictMixin, StatusMixin):
    """Organization resource.
    More info in documentation:
    http://docs.stormpath.com/python/product-guide/#organizations
    """
    autosaves = ('custom_data',)
    writable_attrs = (
        'custom_data',
        'description',
        'name',
        'name_key',
        'status',
    )

    @staticmethod
    def get_resource_attributes():
        from .account import AccountList
        from .account_store_mapping import (
            AccountStoreMapping,
            AccountStoreMappingList,
        )
        from .custom_data import CustomData
        from .group import GroupList
        from .tenant import Tenant

        return {
            'custom_data': CustomData,
            'accounts': AccountList,
            'account_store_mappings': AccountStoreMappingList,
            'default_account_store_mapping': AccountStoreMapping,
            'default_group_store_mapping': AccountStoreMapping,
            'groups': GroupList,
            'tenant': Tenant,
        }

    @property
    def organization_account_store_mappings(self):
        return self._client.organization_account_store_mappings


class OrganizationList(CollectionResource):
    """Organization resource list."""
    create_path = '/organizations'
    resource_class = Organization

    def _ensure_data(self):
        if self.href == '/organizations':
            raise ValueError(
                "It is not possible to access organizations from "
                "Client resource! Try using Tenant resource instead.")

        super(OrganizationList, self)._ensure_data()

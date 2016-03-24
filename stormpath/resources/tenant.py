"""Stormpath Tenant resource mappings."""


from .base import (
    DeleteMixin,
    DictMixin,
    Resource,
    SaveMixin,
    AutoSaveMixin,
)


class Tenant(Resource, DeleteMixin, DictMixin, AutoSaveMixin, SaveMixin):
    """Stormpath Tenant resource.

    More info in documentation:
    http://docs.stormpath.com/python/product-guide/#tenants
    """
    autosaves = ('custom_data',)
    writable_attrs = (
        'custom_data',
        'key',
        'name',
    )

    @staticmethod
    def get_resource_attributes():
        from .account import AccountList
        from .agent import AgentList
        from .application import ApplicationList
        from .custom_data import CustomData
        from .directory import DirectoryList
        from .group import GroupList
        from .id_site import IDSiteList
        from .organization import OrganizationList

        return {
            'accounts': AccountList,
            'agents': AgentList,
            'applications': ApplicationList,
            'custom_data': CustomData,
            'directories': DirectoryList,
            'groups': GroupList,
            'id_sites': IDSiteList,
            'organizations': OrganizationList,
        }

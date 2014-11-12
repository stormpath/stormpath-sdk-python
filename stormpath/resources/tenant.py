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
        from .application import ApplicationList
        from .directory import DirectoryList
        from .custom_data import CustomData
        from .account import AccountList
        from .group import GroupList

        return {
            'custom_data': CustomData,
            'applications': ApplicationList,
            'directories': DirectoryList,
            'accounts': AccountList,
            'groups': GroupList
        }

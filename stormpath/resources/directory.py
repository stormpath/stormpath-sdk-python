"""Stormpath Directory resource mappings."""


from .base import (
    CollectionResource,
    DeleteMixin,
    DictMixin,
    Resource,
    SaveMixin,
    StatusMixin,
    AutoSaveMixin,
)


class Directory(Resource, DeleteMixin, DictMixin, AutoSaveMixin, SaveMixin, StatusMixin):
    """Stormpath Directory resource.

    More info in documentation:
    http://docs.stormpath.com/python/product-guide/#directories
    """
    autosaves = ('provider', 'custom_data',)
    writable_attrs = (
        'custom_data',
        'description',
        'name',
        'provider',
        'status',
    )

    @staticmethod
    def get_resource_attributes():
        from .account import AccountList
        from .group import GroupList
        from .provider import Provider
        from .tenant import Tenant
        from .custom_data import CustomData

        return {
            'custom_data': CustomData,
            'accounts': AccountList,
            'groups': GroupList,
            'provider': Provider,
            'tenant': Tenant,
        }


class DirectoryList(CollectionResource):
    """Directory resource list."""
    create_path = '/directories'
    resource_class = Directory

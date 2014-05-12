"""Stormpath Directory resource mappings."""


from .base import (
    CollectionResource,
    DeleteMixin,
    DictMixin,
    Resource,
    SaveMixin,
    StatusMixin,
)


class Directory(Resource, DeleteMixin, DictMixin, SaveMixin, StatusMixin):
    """Stormpath Directory resource.

    More info in documentation:
    http://docs.stormpath.com/python/product-guide/#directories
    """
    autosaves = ('provider',)
    writable_attrs = (
        'description',
        'name',
        'provider',
        'status',
    )

    def get_resource_attributes(self):
        from .account import AccountList
        from .group import GroupList
        from .provider import Provider
        from .tenant import Tenant

        return {
            'accounts': AccountList,
            'groups': GroupList,
            'provider': Provider,
            'tenant': Tenant,
        }


class DirectoryList(CollectionResource):
    """Directory resource list."""
    create_path = '/directories'
    resource_class = Directory

from .base import (Resource, CollectionResource, StatusMixin,
    SaveMixin, DeleteMixin)


class Directory(Resource, StatusMixin, SaveMixin, DeleteMixin):
    """Directory resource.

    More info in documentation:
    https://www.stormpath.com/docs/python/product-guide#Directories
    """

    writable_attrs = ('name', 'description', 'status')

    def get_resource_attributes(self):
        from .account import AccountList
        from .group import GroupList
        from .tenant import Tenant
        return {
            'tenant': Tenant,
            'accounts': AccountList,
            'groups': GroupList
        }


class DirectoryList(CollectionResource):
    """Directory resource list.
    """
    create_path = '/directories'
    resource_class = Directory

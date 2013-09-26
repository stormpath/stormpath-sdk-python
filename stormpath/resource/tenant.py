from .base import Resource, SaveMixin, DeleteMixin


class Tenant(Resource, SaveMixin, DeleteMixin):
    """Tenant resource.

    More info in documentation:
    https://www.stormpath.com/docs/python/product-guide#DefaultResources
    """

    writable_attrs = ('name', 'key')

    def get_resource_attributes(self):
        from .application import ApplicationList
        from .directory import DirectoryList
        return {
            'applications': ApplicationList,
            'directories': DirectoryList
        }

"""Stormpath Tenant resource mappings."""


from .base import (
    DeleteMixin,
    Resource,
    SaveMixin,
)


class Tenant(Resource, DeleteMixin, SaveMixin):
    """Stormpath Tenant resource.

    More info in documentation:
    https://www.stormpath.com/docs/python/product-guide#DefaultResources
    """
    writable_attrs = (
        'key',
        'name',
    )

    def get_resource_attributes(self):
        from .application import ApplicationList
        from .directory import DirectoryList

        return {
            'applications': ApplicationList,
            'directories': DirectoryList,
        }

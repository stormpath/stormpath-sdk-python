"""Stormpath Tenant resource mappings."""


from .base import (
    DeleteMixin,
    DictMixin,
    Resource,
    SaveMixin,
)


class Tenant(Resource, DeleteMixin, DictMixin, SaveMixin):
    """Stormpath Tenant resource.

    More info in documentation:
    http://docs.stormpath.com/python/product-guide/#tenants
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

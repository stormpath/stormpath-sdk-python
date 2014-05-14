"""Stormpath Tenant resource mappings."""


from .base import (
    DeleteMixin,
    Resource,
    SaveMixin,
)


class Tenant(Resource, DeleteMixin, SaveMixin):
    """Stormpath Tenant resource.

    More info in documentation:
    http://docs.stormpath.com/python/product-guide/#tenants
    """
    writable_attrs = (
        'key',
        'name',
    )

    @staticmethod
    def get_resource_attributes():
        from .application import ApplicationList
        from .directory import DirectoryList

        return {
            'applications': ApplicationList,
            'directories': DirectoryList,
        }

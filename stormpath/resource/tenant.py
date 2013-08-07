from .base import Resource


class Tenant(Resource):
    '''Tenant resource.

    More info in documentation:
    https://www.stormpath.com/docs/python/product-guide#DefaultResources
    '''

    writable_attrs = ('name', 'key')

    def get_resource_attributes(self):
        from .application import ApplicationList
        from .directory import DirectoryList
        return {
            'applications': ApplicationList,
            'directories': DirectoryList
        }

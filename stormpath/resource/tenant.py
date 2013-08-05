from .base import Resource


class Tenant(Resource):

    writable_attrs = ('name', 'key')

    def get_resource_attributes(self):
        from .application import ApplicationList
        from .directory import DirectoryList
        return {
            'applications': ApplicationList,
            'directories': DirectoryList
        }

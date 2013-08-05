from .base import Resource, ResourceList


class Tenant(Resource):

    writable_attrs = ('name', 'key')

    def get_resource_attributes(self):
        from .application import ApplicationList
        from .directory import DirectoryList
        return {
            'applications': ApplicationList,
            'directories': DirectoryList
        }


class TenantList(ResourceList):
    create_path = '/tenants'
    resource_class = Tenant

'''Directory resource.

More info in documentation:
https://www.stormpath.com/docs/python/product-guide#Directories
'''

from .base import Resource, ResourceList, StatusMixin

class Directory(Resource, StatusMixin):

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

    def create_account(self, account, registration_workflow_enabled=None):
        # clever ways of doing this are too clever for their own good
        if registration_workflow_enabled is True:
            registration_workflow_enabled = 'true'
        elif registration_workflow_enabled is False:
            registration_workflow_enabled = 'false'

        return self.accounts.create(account,
            registration_workflow_enabled=registration_workflow_enabled)


class DirectoryList(ResourceList):
    create_path = '/directories'
    resource_class = Directory

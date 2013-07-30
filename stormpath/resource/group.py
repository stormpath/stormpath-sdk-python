from .base import Resource, ResourceList, StatusMixin


class Group(Resource, StatusMixin):
    readwrite_attrs = ('name', 'description', 'status')

    def get_resource_attributes(self):
        from .tenant import Tenant
        from .directory import Directory
        from .account import AccountList

        return {
            'tenant': Tenant,
            'directory': Directory,
            'accounts': AccountList
        }

    def add_account(self, account):
        return self._client.group_memberships.create({
            'group': self,
            'account': account
        })


class GroupList(ResourceList):
    resource_class = Group

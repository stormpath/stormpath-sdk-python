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


class GroupList(ResourceList):
    resource_class = Group

    def add_account(self, account):
        self._client.group_memberships.create({
            'group': self,
            'account': account
        })

from .base import Resource, ResourceList, StatusMixin


class Group(Resource, StatusMixin):
    writable_attrs = ('name', 'description', 'status')

    def get_resource_attributes(self):
        from .tenant import Tenant
        from .directory import Directory
        from .account import AccountList
        from .group_membership import GroupMembershipList

        return {
            'tenant': Tenant,
            'directory': Directory,
            'accounts': AccountList,
            'account_memberships': GroupMembershipList
        }

    def add_account(self, account):
        return self._client.group_memberships.create({
            'group': self,
            'account': account
        })


class GroupList(ResourceList):
    resource_class = Group

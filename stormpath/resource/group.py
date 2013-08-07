from .base import Resource, ResourceList, StatusMixin


class Group(Resource, StatusMixin):
    '''Group resource.

    More info in documentation:
    https://www.stormpath.com/docs/python/product-guide#Groups
    '''

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
    """Group resource list.
    """
    resource_class = Group

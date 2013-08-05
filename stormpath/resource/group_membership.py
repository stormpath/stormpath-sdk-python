from .base import Resource, ResourceList


class GroupMembership(Resource):
    writable_attrs = ('account', 'group')

    def get_resource_attributes(self):
        from .account import Account
        from .group import Group
        return {
            'account': Account,
            'group': Group
        }


class GroupMembershipList(ResourceList):
    resource_class = GroupMembership

from .base import Resource, ResourceList


class GroupMembership(Resource):
    '''GroupMembership resource.

    More info in documentation:
    https://www.stormpath.com/docs/python/product-guide#AssignAccountGroup
    '''

    writable_attrs = ('account', 'group')

    def get_resource_attributes(self):
        from .account import Account
        from .group import Group
        return {
            'account': Account,
            'group': Group
        }


class GroupMembershipList(ResourceList):
    """Group membership resource list.
    """
    resource_class = GroupMembership

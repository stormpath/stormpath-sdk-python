from .base import Resource, CollectionResource, DeleteMixin


class GroupMembership(Resource, DeleteMixin):
    """GroupMembership resource.

    More info in documentation:
    https://www.stormpath.com/docs/python/product-guide#AssignAccountGroup
    """

    writable_attrs = ('account', 'group')

    def get_resource_attributes(self):
        from .account import Account
        from .group import Group
        return {
            'account': Account,
            'group': Group
        }


class GroupMembershipList(CollectionResource):
    """Group membership resource list.
    """
    resource_class = GroupMembership

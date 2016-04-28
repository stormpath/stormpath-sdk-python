"""Stormpath Directory resource mappings."""


from .base import (
    CollectionResource,
    DeleteMixin,
    Resource,
)


class GroupMembership(Resource, DeleteMixin):
    """Stormpath GroupMembership resource.

    More info in documentation:
    http://docs.stormpath.com/python/product-guide/#create-a-group-membership
    """
    writable_attrs = (
        'account',
        'group',
    )

    @staticmethod
    def get_resource_attributes():
        from .account import Account
        from .group import Group

        return {
            'account': Account,
            'group': Group,
        }


class GroupMembershipList(CollectionResource):
    """GroupMembership resource list."""

    create_path = '/groupMemberships'
    resource_class = GroupMembership

    def _ensure_data(self):
        if self.href == '/groupMemberships':
            raise ValueError(
                "It is not possible to access group_memberships from the "
                "Client resource! Try using the Account resource instead.")

        super(GroupMembershipList, self)._ensure_data()

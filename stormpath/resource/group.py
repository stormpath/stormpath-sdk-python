"""Stormpath Directory resource mappings."""


from .base import (
    AutoSaveMixin,
    CollectionResource,
    DeleteMixin,
    Resource,
    StatusMixin,
)


class Group(Resource, AutoSaveMixin, DeleteMixin, StatusMixin):
    """Group resource.

    More info in documentation:
    http://docs.stormpath.com/python/product-guide/#groups
    """
    autosaves = ('custom_data',)
    writable_attrs = (
        'custom_data',
        'description',
        'name',
        'status',
    )

    def get_resource_attributes(self):
        from .account import AccountList
        from .custom_data import CustomData
        from .directory import Directory
        from .group_membership import GroupMembershipList
        from .tenant import Tenant

        return {
            'accounts': AccountList,
            'account_memberships': GroupMembershipList,
            'custom_data': CustomData,
            'directory': Directory,
            'tenant': Tenant,
        }

    def add_account(self, account):
        """Associate an Account with the Group.

        This creates a
        :class:`stormpath.resource.group_membership.GroupMembership`.

        :param account: A :class:`stormpath.resource.account.Account` object

        """
        return self._client.group_memberships.create({
            'group': self,
            'account': account
        })


class GroupList(CollectionResource):
    """Group resource list.
    """
    resource_class = Group

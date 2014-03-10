"""Stormpath Account resource mappings."""


from .base import (
    AutoSaveMixin,
    CollectionResource,
    DeleteMixin,
    Resource,
    StatusMixin,
)


class Account(Resource, AutoSaveMixin, DeleteMixin, StatusMixin):
    """Account resource.

    More info in documentation:
    http://docs.stormpath.com/python/product-guide/#accounts
    """
    autosaves = ('custom_data',)
    writable_attrs = (
        'custom_data',
        'email',
        'given_name',
        'middle_name',
        'password',
        'status',
        'surname',
        'username',
    )
    STATUS_UNVERIFIED = 'UNVERIFIED'

    def __str__(self):
        return self.username

    def get_resource_attributes(self):
        from .custom_data import CustomData
        from .directory import Directory
        from .group import GroupList
        from .group_membership import GroupMembershipList
        from .tenant import Tenant

        return {
            'custom_data': CustomData,
            'directory': Directory,
            'email_verification_token': Resource,
            'groups': GroupList,
            'group_memberships': GroupMembershipList,
            'tenant': Tenant,
        }

    def add_group(self, group):
        """Associate a Group with this Account.

        This creates a
        :class:`stormpath.resources.group_membership.GroupMembership` resource
        on the backend.

        :param group: A :class:`stormpath.resources.group.Group` object.
        """
        return self._client.group_memberships.create({
            'account': self,
            'group': group,
        })

    def in_group(self, group):
        """Check to see whether or not this Account is a member of the
        specified Group.

        :param group: A :class:`stormpath.resources.group.Group` object.

        :returns: True if the Account is a member of the Group, False
            otherwise.
        """
        for g in self.groups.search(group.name):
            if g.name == group.name:
                return True

        return False

    def in_groups(self, groups, all=True):
        """Check to see whether or not this Account is a member of a list of
        Groups.

        :param groups: A list of :class:`stormpath.resources.group.Group`
            objects to check.
        :param all: A boolean (default: True) which controls how Group
            assertions are handled.  If all is set to True (default), then
            we'll check to ensure that this Account is a member of ALL Groups
            before returning True.  If all is False, we'll return True if this
            Account is a member of ANY of the Groups in the list.

        :returns: True if the Group checks pass, False otherwise.
        """
        total_checks = 0

        for group in groups:
            if self.in_group(group):
                total_checks += 1

                if not all:
                    return True

        return True if all and total_checks == len(groups) else False

    def is_unverified(self):
        """Check if Account is unverified.

        An Account is unverified if the workflow automation is such that it
        requires verification before enabling the Account.

        More info in documentation:
        http://docs.stormpath.com/console/product-guide/#cloud-directory-workflow-automations
        """
        return self.get_status() == self.STATUS_UNVERIFIED


class AccountList(CollectionResource):
    """Stormpath Account resource list."""
    resource_class = Account

    def verify_email_token(self, token):
        """Verify this Account by using a token.

        :param token: Account verification token.
        """
        href = '/accounts/emailVerificationTokens/' + token
        data = self._store.create_resource(href, {})

        return self.resource_class(client=self._client, properties=data)

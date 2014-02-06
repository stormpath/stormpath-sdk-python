"""Stormpath Account resource mappings."""


from .base import (
    AutoSaveMixin,
    CollectionResource,
    DeleteMixin,
    Resource,
    StatusMixin,
)


class Account(AutoSaveMixin, DeleteMixin, Resource, StatusMixin):
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
            'tenant': Tenant,
            'directory': Directory,
            'groups': GroupList,
            'group_memberships': GroupMembershipList,
            'email_verification_token': Resource,
            'custom_data': CustomData
        }

    def add_group(self, group):
        """Associate a Group with this Account.

        This creates a
        :class:`stormpath.resource.group_membership.GroupMembership` resource
        on the backend.

        :param group: A :class:`stormpath.resource.group.Group` object.
        """
        return self._client.group_memberships.create({
            'account': self,
            'group': group,
        })

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

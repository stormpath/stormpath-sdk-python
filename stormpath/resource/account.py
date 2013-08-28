from .base import Resource, ResourceList, StatusMixin


class Account(Resource, StatusMixin):
    """Account resource.

    More info in documentation:
    https://www.stormpath.com/docs/python/product-guide#Accounts
    """

    STATUS_UNVERIFIED = 'UNVERIFIED'

    writable_attrs = ('username', 'password', 'email', 'given_name',
        'middle_name', 'surname', 'full_name', 'status')

    def get_resource_attributes(self):
        from .directory import Directory
        from .group import GroupList
        from .group_membership import GroupMembershipList
        from .tenant import Tenant
        return {
            'tenant': Tenant,
            'directory': Directory,
            'groups': GroupList,
            'group_memberships': GroupMembershipList,
            'email_verification_token': Resource
        }

    def __str__(self):
        return self.username

    def add_group(self, group):
        """Associate a Group with the Account

        This creates a
        :class:`stormpath.resource.group_membership.GroupMembership`.

        :param group: A :class:`stormpath.resource.group.Group` object

        """

        return self._client.group_memberships.create({
            'account': self,
            'group': group
        })

    def is_unverified(self):
        """Check if Account is unverified.

        An Account is unverified if the workflow automation is such that it
        requires verification before enabling the Account.

        More info in documentation:
        http://www.stormpath.com/docs/rest/product-guide#AccountRegistration

        """
        return self.get_status() == self.STATUS_UNVERIFIED


class AccountList(ResourceList):
    """Account resource list.
    """
    resource_class = Account

    def verify_email_token(self, token):
        """Verify account by using a token

        :param token: account verification token

        """
        href = '/accounts/emailVerificationTokens/' + token
        data = self._store.create_resource(href, {})

        return self.resource_class(properties=data, client=self._client)

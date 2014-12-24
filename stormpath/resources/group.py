"""Stormpath Directory resource mappings."""


from six import string_types

from stormpath.error import Error as StormpathError

from .base import (
    AutoSaveMixin,
    CollectionResource,
    DeleteMixin,
    DictMixin,
    Resource,
    StatusMixin,
)


class Group(Resource, AutoSaveMixin, DeleteMixin, DictMixin, StatusMixin):
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

    @staticmethod
    def get_resource_attributes():
        from .account import AccountList
        from .custom_data import CustomData
        from .directory import Directory
        from .group_membership import GroupMembershipList
        from .tenant import Tenant

        return {
            'custom_data': CustomData,
            'accounts': AccountList,
            'account_memberships': GroupMembershipList,
            'directory': Directory,
            'tenant': Tenant,
        }

    def _resolve_account(self, resolvable):
        """Given an Account object or href or name, return a functional Account
        object.

        This helper method allows us to easily accept Account arguments in
        multiple ways.

        :param resolvable: This could be any one of the following:

            - An :class:`stormpath.resources.account.Account` object, that
              already exists in Stormpath.
            - An Account href, ex:
              'https://api.stormpath.com/v1/accounts/3wzkqr03K8WxRp8NQuYSs3'
            - An Account username, ex: 'rdegges'.
            - An Account email, ex: 'randall@stormpath.com'.
            - A search query, ex: {'username': '*rdegges*'}.

        :raises:
            - ValueError if an invalid href, username, or email is specified.
            - TypeError if a non-Account object is specified.

        :rtype: obj
        :returns: A matching Account object.

        .. note::
            Passing in an :class:`stormpath.resources.account.Account` object
            will always be the quickest way to add an Account, as it doesn't
            require any additional API calls.
        """
        from .account import Account

        # If this is an Account object already, we have no work to do!
        if isinstance(resolvable, Account):
            return resolvable

        # Check to see whether or not this is a string.
        if isinstance(resolvable, string_types):

            # If this Account is an href, we'll just use that.
            if resolvable.startswith(self._client.BASE_URL):
                try:
                    account = self.directory.accounts.get(resolvable)

                    # We're accessing account.username here to force evaluation
                    # of this Account -- this allows us to check and see
                    # whether or not this Account is actually valid.
                    account.username
                except StormpathError:
                    raise ValueError('Invalid Account href specified.')

                return account

            # Otherwise, we'll assume this is an Account username or email, and
            # try to query it.
            else:
                for attr in ['username', 'email']:
                    for a in self.directory.accounts.search({
                        attr: resolvable,
                    }):
                        if getattr(a, attr) == resolvable:
                            return a

                raise ValueError('Invalid Account specified.')

        # Check to see whether or not this is a dictionary -- if it is, this
        # means the user is specifying their own search criteria.
        if isinstance(resolvable, dict):
            try:
                for account in self.directory.accounts.search(resolvable):
                    return account

                raise StormpathError
            except StormpathError:
                raise ValueError('Invalid search criteria specified.')

        # If this is not a string instance, something horrible was given to us,
        # so bail.
        raise TypeError('Unsupported type. Account object, href, username, or email required.')

    def add_account(self, resolvable):
        """Associate an Account with this Group.

        This creates a
        :class:`stormpath.resources.group_membership.GroupMembership` object in
        the backend.

        :param resolvable: This could be any one of the following:

            - An :class:`stormpath.resources.account.Account` object.
            - An Account href, ex:
                'https://api.stormpath.com/v1/accounts/3wzkqr03K8WxRp8NQuYSs3'
            - An Account username, ex: 'rdegges'.
            - An Account email, ex: 'randall@stormpath.com'.
            - A search query, ex: {'username': '*rdegges*'}.

        .. note::
            Passing in a :class:`stormpath.resources.account.Account` object
            will always be the quickest way to add an Account, as it doesn't
            require any additional API calls.
        """
        account = self._resolve_account(resolvable)
        return self._client.group_memberships.create({
            'account': account,
            'group': self,
        })

    def add_accounts(self, resolvables):
        """Associate Accounts with this Group.

        This creates a
        :class:`stormpath.resources.group_membership.GroupMembership` object in
        the backend.

        :param resolvables: A list of either:

            - An :class:`stormpath.resources.account.Account` object.
            - An Account href, ex:
                'https://api.stormpath.com/v1/accounts/3wzkqr03K8WxRp8NQuYSs3'
            - An Account username, ex: 'rdegges'.
            - An Account email, ex: 'randall@stormpath.com'.
            - A search query, ex: {'username': '*rdegges*'}.

        .. note::
            Passing in a :class:`stormpath.resources.account.Account` object
            will always be the quickest way to add an Account, as it doesn't
            require any additional API calls.
        """
        for a in [self._resolve_account(account) for account in resolvables]:
            self._client.group_memberships.create({
                'account': a,
                'group': self,
            })

    def remove_account(self, resolvable):
        """Remove this Account from the specified Group.

        :param resolvable: This could be any one of the following:

            - An :class:`stormpath.resources.account.Account` object.
            - An Account href, ex:
                'https://api.stormpath.com/v1/accounts/3wzkqr03K8WxRp8NQuYSs3'
            - An account username, ex: 'rdegges'.
            - An account email, ex: 'randall@stormpath.com'.
            - A search query, ex: {'username': '*rdegges*'}.

        :raises: :class:`stormpath.error.StormpathError` if the Account specified
            is not part of this Group.

        .. note::
            Passing in a :class:`stormpath.resources.group.Account` object will
            always be the quickest way to remove an Account, since it doesn't
            require any additional API calls.
        """
        account = self._resolve_account(resolvable)

        for membership in self.account_memberships:
            if membership.account.href == account.href:
                membership.delete()
                return

        raise StormpathError({
            'developerMessage': 'This user is not part of Group %s.' % self.name,
        })

    def remove_accounts(self, resolvables):
        """Remove Accounts from the specified Group.

        :param resolvables: A list of either:

            - An :class:`stormpath.resources.account.Account` object.
            - An Account href, ex:
                'https://api.stormpath.com/v1/accounts/3wzkqr03K8WxRp8NQuYSs3'
            - An account username, ex: 'rdegges'.
            - An account email, ex: 'randall@stormpath.com'.
            - A search query, ex: {'username': '*rdegges*'}.

        :raises: :class:`stormpath.error.StormpathError` if the Accounts
            specified are not part of this Group.

        .. note::
            Passing in a :class:`stormpath.resources.group.Account` object will
            always be the quickest way to remove an Account, since it doesn't
            require any additional API calls.
        """
        memberships = [membership for membership in self.account_memberships]

        for a in [self._resolve_account(account) for account in resolvables]:
            done = False
            for membership in memberships:
                if membership.account.href == a.href:
                    membership.delete()
                    done = True

            if not done:
                raise StormpathError({
                    'developerMessage': 'This user is not part of Group %s.' % self.name,
                })

    def has_account(self, resolvable):
        """Check to see whether or not this Group contains the specified
        Account.

        :param resolvable: This could be any one of the following:

            - An :class:`stormpath.resources.account.Account` object.
            - An Account href, ex:
                'https://api.stormpath.com/v1/accounts/3wzkqr03K8WxRp8NQuYSs3'
            - An account username, ex: 'rdegges'.
            - An account email, ex: 'randall@stormpath.com'.
            - A search query, ex: {'username': '*rdegges*'}.

        :returns: True if the Account is a member of this Group, False
            otherwise.

        .. note::
            Passing in a :class:`stormpath.resources.group.Account` object will
            always be the quickest way to check an Account's membership, since
            it doesn't require any additional API calls.
        """
        account = self._resolve_account(resolvable)

        for a in self.accounts.query(username=account.username):
            if a.username == account.username:
                return True

        return False

    def has_accounts(self, resolvable, all=True):
        """Check to see whether or not this Group contains the specified list
        of Accounts.

        :param resolvable: A list of either:

            - :class:`stormpath.resources.group.Account` objects.
            - Account hrefs, ex:
                'https://api.stormpath.com/v1/accounts/3wzkqr03K8WxRp8NQuYSs3'
            - Account usernames, ex: 'rdegges'.
            - Account emails, ex: 'randall@stormpath.com'.
            - A search query, ex: {'username': '*rdegges*'}.

                This could look something like:

                [
                    account,
                    'https://api.stormpath.com/v1/accounts/3wzkqr03K8WxRp8NQuYSs3',
                    'rdegges',
                    'randall@stormpath.com',
                    {'username': '*rdegges*'},
                ]

        :param all: A boolean (default: True) which controls how Account
            assertions are handled.  If all is set to True (default), then
            we'll check to ensure that this Group contains ALL Accounts
            before returning True.  If all is False, we'll return True if this
            Group contains ANY of the Accounts in the list.

        :returns: True if the Account checks pass, False otherwise.
        """
        total_checks = 0

        for account in resolvable:
            if self.has_account(account):
                total_checks += 1

                if not all:
                    return True

        return True if all and total_checks == len(resolvable) else False


class GroupList(CollectionResource):
    """Group resource list."""
    resource_class = Group

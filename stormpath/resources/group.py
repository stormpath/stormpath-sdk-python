"""Stormpath Directory resource mappings."""


from six import string_types

from stormpath.error import Error as StormpathError

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

    def _resolve_account(self, account_object_or_href_or_name):
        """Given an Account object or href or name, return a functional Account
        object.

        This helper method allows us to easily accept Account arguments in
        multiple ways.

        :param account_object_or_href_or_name: This could be any one of the
            following:

            - An :class:`stormpath.resources.account.Account` object.
            - An Account href, ex:
                'https://api.stormpath.com/v1/accounts/3wzkqr03K8WxRp8NQuYSs3'
            - An Account username, ex: 'rdegges'.
            - An Account email, ex: 'randall@stormpath.com'.

        :raises: ValueError if an invalid href or name is specified, or
            TypeError if a non-Account object is specified.

        .. note::
            Passing in an :class:`stormpath.resources.account.Account` object
            will always be the quickest way to add an Account, as it doesn't
            require any additional API calls.
        """
        from .account import Account

        # First, we'll check to see whether or not this is a string.
        account = account_object_or_href_or_name
        if isinstance(account, string_types):

            # If this Account is an href, we'll just use that.
            if account.startswith('https://api.stormpath.com/'):
                try:
                    account = self.directory.accounts.get(account)

                    # We're accessing account.username here to force evaluation
                    # of this Account -- this allows us to check and see
                    # whether or not this Account is actually valid.
                    account.username
                except StormpathError:
                    raise ValueError('Invalid Account href specified.')

            # Otherwise, we'll assume this is an Account username or email, and
            # try to query it.
            else:
                for attr in ['username', 'email']:
                    for a in self.directory.accounts.search({attr: account}):
                        if getattr(a, attr) == account:
                            return a

                raise ValueError('Invalid Account %s specified.' % attr)

        # If this is not a Group instance, something horrible was given to us,
        # so bail.
        elif not isinstance(account, Account):
            raise TypeError('Unsupported type. Account object required.')

        return account

        """Associate an Account with this Group.

        This creates a
        :class:`stormpath.resources.group_membership.GroupMembership` object in
        the backend.

        :param account: A :class:`stormpath.resources.account.Account` object.
        """
        return self._client.group_memberships.create({
            'account': account,
            'group': self,
        })


class GroupList(CollectionResource):
    """Group resource list."""
    resource_class = Group

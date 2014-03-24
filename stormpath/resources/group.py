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

        :raises:
            - ValueError if an invalid href or name is specified.
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
        if isinstance(account_object_or_href_or_name, Account):
            return account_object_or_href_or_name

        # We now know this isn't an Account object.
        href_or_name = account_object_or_href_or_name

        # Check to see whether or not this is a string.
        if isinstance(href_or_name, string_types):

            # If this Account is an href, we'll just use that.
            if href_or_name.startswith(self._client.BASE_URL):
                href = href_or_name

                try:
                    account = self.directory.accounts.get(href)

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
                name = href_or_name

                for attr in ['username', 'email']:
                    for a in self.directory.accounts.search({attr: name}):
                        if getattr(a, attr) == name:
                            return a

                raise ValueError('Invalid Account %s specified.' % attr)

        # If this is not a string instance, something horrible was given to us,
        # so bail.
        raise TypeError('Unsupported type. Account object required.')

    def add_account(self, account_object_or_href_or_name):
        """Associate an Account with this Group.

        This creates a
        :class:`stormpath.resources.group_membership.GroupMembership` object in
        the backend.

        :param account_object_or_href_or_name: This could be any one of the
            following:

            - An :class:`stormpath.resources.account.Account` object.
            - An Account href, ex:
                'https://api.stormpath.com/v1/accounts/3wzkqr03K8WxRp8NQuYSs3'
            - An Account username, ex: 'rdegges'.
            - An Account email, ex: 'randall@stormpath.com'.

        .. note::
            Passing in a :class:`stormpath.resources.account.Account` object
            will always be the quickest way to add an Account, as it doesn't
            require any additional API calls.
        """
        account = self._resolve_account(account_object_or_href_or_name)
        return self._client.group_memberships.create({
            'account': account,
            'group': self,
        })

    def remove_account(self, account_object_or_href_or_name):
        """Remove this Account from the specified Group.

        :param account_object_or_href_or_name: This could be any one of the
            following:

            - An :class:`stormpath.resources.account.Account` object.
            - An Account href, ex:
                'https://api.stormpath.com/v1/accounts/3wzkqr03K8WxRp8NQuYSs3'
            - An account username, ex: 'rdegges'.
            - An account email, ex: 'randall@stormpath.com'.

        :raises: :class:`stormpath.error.StormpathError` if the Account specified
            is not part of this Group.

        .. note::
            Passing in a :class:`stormpath.resources.group.Account` object will
            always be the quickest way to remove an Account, since it doesn't
            require any additional API calls.
        """
        account = self._resolve_account(account_object_or_href_or_name)

        for membership in self.account_memberships:
            if membership.account.href == account.href:
                membership.delete()
                return

        raise StormpathError({
            'developerMessage': 'This user is not part of Group %s.' % self.name,
        })


class GroupList(CollectionResource):
    """Group resource list."""
    resource_class = Group

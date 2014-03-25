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

    def _resolve_account(self, account_object_or_href_or_username_or_email):
        """Given an Account object or href or name, return a functional Account
        object.

        This helper method allows us to easily accept Account arguments in
        multiple ways.

        :param account_object_or_href_or_username_or_email: This could be any
            one of the following:

            - An :class:`stormpath.resources.account.Account` object, that
              already exists in Stormpath.
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
        if isinstance(account_object_or_href_or_username_or_email, Account):
            return account_object_or_href_or_username_or_email

        # We now know this isn't an Account object.
        href_or_username_or_email = account_object_or_href_or_username_or_email

        # Check to see whether or not this is a string.
        if isinstance(href_or_username_or_email, string_types):

            # If this Account is an href, we'll just use that.
            if href_or_username_or_email.startswith(self._client.BASE_URL):
                href = href_or_username_or_email

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
                username_or_email = href_or_username_or_email

                for attr in ['username', 'email']:
                    for a in self.directory.accounts.search({
                        attr: username_or_email,
                    }):
                        if getattr(a, attr) == username_or_email:
                            return a

                raise ValueError('Invalid Account %s specified.' % attr)

        # If this is not a string instance, something horrible was given to us,
        # so bail.
        raise TypeError('Unsupported type. Account object, href, username, or email required.')

    def add_account(self, account_object_or_href_or_username_or_email):
        """Associate an Account with this Group.

        This creates a
        :class:`stormpath.resources.group_membership.GroupMembership` object in
        the backend.

        :param account_object_or_href_or_username_or_email: This could be any
            one of the following:

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
        account = self._resolve_account(account_object_or_href_or_username_or_email)
        return self._client.group_memberships.create({
            'account': account,
            'group': self,
        })

    def remove_account(self, account_object_or_href_or_username_or_email):
        """Remove this Account from the specified Group.

        :param account_object_or_href_or_username_or_email: This could be any
            one of the following:

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
        account = self._resolve_account(account_object_or_href_or_username_or_email)

        for membership in self.account_memberships:
            if membership.account.href == account.href:
                membership.delete()
                return

        raise StormpathError({
            'developerMessage': 'This user is not part of Group %s.' % self.name,
        })

    def has_account(self, account_object_or_href_or_username_or_email):
        """Check to see whether or not this Group contains the specified
        Account.

        :param account_object_or_href_or_username_or_email: This could be any
            one of the following:

            - An :class:`stormpath.resources.account.Account` object.
            - An Account href, ex:
                'https://api.stormpath.com/v1/accounts/3wzkqr03K8WxRp8NQuYSs3'
            - An account username, ex: 'rdegges'.
            - An account email, ex: 'randall@stormpath.com'.

        :returns: True if the Account is a member of this Group, False
            otherwise.

        .. note::
            Passing in a :class:`stormpath.resources.group.Account` object will
            always be the quickest way to check an Account's membership, since
            it doesn't require any additional API calls.
        """
        account = self._resolve_account(account_object_or_href_or_username_or_email)

        for a in self.accounts.query(username=account.username):
            if a.username == account.username:
                return True

        return False

    def has_accounts(self, account_objects_or_hrefs_or_usernames_or_emails, all=True):
        """Check to see whether or not this Group contains the specified list
        of Accounts.

        :param account_objects_or_hrefs_or_usernames_or_emails: A list of
            either:

            - :class:`stormpath.resources.group.Account` objects.
            - Account hrefs, ex:
                'https://api.stormpath.com/v1/accounts/3wzkqr03K8WxRp8NQuYSs3'
            - Account usernames, ex: 'admins'.
            - Account emails, ex: 'randall@stormpath.com'.

        :param all: A boolean (default: True) which controls how Account
            assertions are handled.  If all is set to True (default), then
            we'll check to ensure that this Group contains ALL Accounts
            before returning True.  If all is False, we'll return True if this
            Group contains ANY of the Accounts in the list.

        :returns: True if the Account checks pass, False otherwise.
        """
        total_checks = 0

        accounts = account_objects_or_hrefs_or_usernames_or_emails
        for account in accounts:
            if self.has_account(account):
                total_checks += 1

                if not all:
                    return True

        return True if all and total_checks == len(accounts) else False


class GroupList(CollectionResource):
    """Group resource list."""
    resource_class = Group

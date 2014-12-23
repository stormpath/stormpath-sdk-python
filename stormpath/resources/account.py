"""Stormpath Account resource mappings."""


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


class Account(Resource, AutoSaveMixin, DictMixin, DeleteMixin, StatusMixin):
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
        'provider_data',
        'status',
        'surname',
        'username',
    )
    resolvable_attrs = (
        'username',
        'email',
    )
    STATUS_UNVERIFIED = 'UNVERIFIED'

    def __str__(self):
        return self.username

    @property
    def is_new_account(self):
        return self.sp_http_status == 201

    @staticmethod
    def get_resource_attributes():
        from .custom_data import CustomData
        from .directory import Directory
        from .group import GroupList
        from .group_membership import GroupMembershipList
        from .provider_data import ProviderData
        from .tenant import Tenant
        from .api_key import ApiKeyList

        return {
            'custom_data': CustomData,
            'directory': Directory,
            'email_verification_token': Resource,
            'groups': GroupList,
            'group_memberships': GroupMembershipList,
            'provider_data': ProviderData,
            'tenant': Tenant,
            'api_keys': ApiKeyList,
        }

    def _resolve_group(self, resolvable):
        """Given a Group object or href or name, return a functional Group
        object.

        This helper method allows us to easily accept Group arguments in
        multiple ways.

        :param resolvable: This could be any one of the following:

            - A :class:`stormpath.resources.group.Group` object, that already
              exists in Stormpath.
            - A Group href, ex:
              'https://api.stormpath.com/v1/groups/3wzkqr03K8WxRp8NQuYSs3'
            - A Group name, ex: 'admins'.

        :raises:
            - ValueError if an invalid href or name is specified.
            - TypeError if a non-Group object is specified.

        :rtype: obj
        :returns: A matching Group object.

        .. note::
            Passing in a :class:`stormpath.resources.group.Group` object will
            always be the quickest way to add a Group, as it doesn't require
            any additional API calls.
        """
        from .group import Group

        # If this is a Group object already, we have no work to do!
        if isinstance(resolvable, Group):
            return resolvable

        # We now know this isn't a Group object.
        href_or_name = resolvable

        # Check to see whether or not this is a string.
        if isinstance(resolvable, string_types):

            # If this Group is an href, we'll just use that.
            if href_or_name.startswith(self._client.BASE_URL):
                href = href_or_name

                try:
                    group = self.directory.groups.get(href)

                    # We're accessing group.name here to force evaluation of
                    # this Group -- this allows us to check and see whether or
                    # not this Group is actually valid.
                    group.name
                except StormpathError:
                    raise ValueError('Invalid Group href specified.')

                return group

            # Otherwise, we'll assume this is a Group name, and try to query
            # it.
            else:
                name = href_or_name
                groups = self.directory.groups.query(name=name)

                for g in groups:
                    if g.name == name:
                        return g

                raise ValueError('Invalid Group name specified.')

        # If this is not a string instance, something horrible was given to us,
        # so bail.
        raise TypeError('Unsupported type. Group object, href, or name required.')

    def add_group(self, resolvable):
        """Associate a Group with this Account.

        This creates a
        :class:`stormpath.resources.group_membership.GroupMembership` resource
        on the backend.

        :param resolvable: This could be any one of the following:

            - A :class:`stormpath.resources.group.Group` object.
            - A Group href, ex:
                'https://api.stormpath.com/v1/groups/3wzkqr03K8WxRp8NQuYSs3'
            - A Group name, ex: 'admins'.

        .. note::
            Passing in a :class:`stormpath.resources.group.Group` object will
            always be the quickest way to add a Group, as it doesn't require
            any additional API calls.
        """
        group = self._resolve_group(resolvable)
        return self._client.group_memberships.create({
            'account': self,
            'group': group,
        })

    def has_group(self, resolvable):
        """Check to see whether or not this Account is a member of the
        specified Group.

        :param resolvable: This could be any one of the following:

            - A :class:`stormpath.resources.group.Group` object.
            - A Group href, ex:
                'https://api.stormpath.com/v1/groups/3wzkqr03K8WxRp8NQuYSs3'
            - A Group name, ex: 'admins'.

        .. note::
            Passing in a :class:`stormpath.resources.group.Group` object will
            always be the quickest way to check a Group's membership, since it
            doesn't require any additional API calls.

        :returns: True if the Account is a member of the Group, False
            otherwise.
        """
        group = self._resolve_group(resolvable)

        for g in self.groups.query(name=group.name):
            if g.name == group.name:
                return True

        return False

    def has_groups(self, resolvables, all=True):
        """Check to see whether or not this Account is a member of a list of
        Groups.

        :param resolvables: A list of either:

            - :class:`stormpath.resources.group.Group` objects.
            - Group hrefs, ex:
                'https://api.stormpath.com/v1/groups/3wzkqr03K8WxRp8NQuYSs3'
            - Group names, ex: 'admins'.

                This could look something like:

                [
                    group,
                    'https://api.stormpath.com/v1/groups/3wzkqr03K8WxRp8NQuYSs3',
                    'admins',
                ]

        :param all: A boolean (default: True) which controls how Group
            assertions are handled.  If all is set to True (default), then
            we'll check to ensure that this Account is a member of ALL Groups
            before returning True.  If all is False, we'll return True if this
            Account is a member of ANY of the Groups in the list.

        :returns: True if the Group checks pass, False otherwise.
        """
        total_checks = 0

        for group in resolvables:
            if self.has_group(group):
                total_checks += 1

                if not all:
                    return True

        return True if all and total_checks == len(resolvables) else False

    def is_unverified(self):
        """Check if Account is unverified.

        An Account is unverified if the workflow automation is such that it
        requires verification before enabling the Account.

        More info in documentation:
        http://docs.stormpath.com/console/product-guide/#cloud-directory-workflow-automations
        """
        return self.get_status() == self.STATUS_UNVERIFIED

    def remove_group(self, resolvable):
        """Remove this Account from the specified Group.

        :param resolvable: This could be any one of the following:

            - A :class:`stormpath.resources.group.Group` object.
            - A Group href, ex:
                'https://api.stormpath.com/v1/groups/3wzkqr03K8WxRp8NQuYSs3'
            - A Group name, ex: 'admins'.

        :raises: :class:`stormpath.error.StormpathError` if the Group specified
            does not contain this Account.

        .. note::
            Passing in a :class:`stormpath.resources.group.Group` object will
            always be the quickest way to check a Group's membership, since it
            doesn't require any additional API calls.
        """
        group = self._resolve_group(resolvable)

        for membership in self.group_memberships:
            if membership.group.href == group.href:
                membership.delete()
                return

        raise StormpathError({
            'developerMessage': 'This user is not part of Group %s.' % group.name,
        })


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

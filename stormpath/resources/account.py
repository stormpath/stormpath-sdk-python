"""Stormpath Account resource mappings."""


from six import string_types

from stormpath.error import Error as StormpathError
from .base import (
    SIGNAL_RESOURCE_CREATED,
    AutoSaveMixin,
    CollectionResource,
    DeleteMixin,
    DictMixin,
    Resource,
    StatusMixin,
)

from pydispatch import dispatcher


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
    STATUS_UNVERIFIED = 'UNVERIFIED'

    def __str__(self):
        return self.username

    @property
    def is_new_account(self):
        return self.sp_http_status == 201

    @staticmethod
    def get_resource_attributes():
        from .application import ApplicationList
        from .custom_data import CustomData
        from .directory import Directory
        from .group import GroupList
        from .group_membership import GroupMembershipList
        from .provider_data import ProviderData
        from .tenant import Tenant
        from .api_key import ApiKeyList

        return {
            'applications': ApplicationList,
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
        """Given a Group object or href, name, or search query, return a
        functional Group object.

        This helper method allows us to easily accept Group arguments in
        multiple ways.

        :param resolvable: This could be any one of the following:

            - A :class:`stormpath.resources.group.Group` object, that already
              exists in Stormpath.
            - A Group href, ex:
              'https://api.stormpath.com/v1/groups/3wzkqr03K8WxRp8NQuYSs3'
            - A Group name, ex: 'admins'.
            - A search query, ex: {'name': '*_admins'}.

        :raises:
            - ValueError if an invalid href, name, or search query is specified.
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

        # Check to see whether or not this is a string.
        if isinstance(resolvable, string_types):

            # If this Group is an href, we'll just use that.
            if resolvable.startswith(self._client.BASE_URL):
                try:
                    group = self.directory.groups.get(resolvable)

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
                groups = self.directory.groups.query(name=resolvable)

                for g in groups:
                    if g.name == resolvable:
                        return g

                raise ValueError('Invalid Group name specified.')

        # Check to see whether or not this is a dictionary -- if it is, this
        # means the user is specifying their own search criteria.
        if isinstance(resolvable, dict):
            try:
                for group in self.directory.groups.search(resolvable):
                    return group

                raise StormpathError
            except StormpathError:
                raise ValueError('Invalid search criteria specified.')

        # If this is not a string instance, something horrible was given to us,
        # so bail.
        raise TypeError('Unsupported type. Group object, href, name, or search query required.')

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
            - A search query, ex: {'name': '*_admins'}.

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

    def add_groups(self, resolvables):
        """Associate a list of Groups with this Account.

        :param resolvables: A list of either:

            - :class:`stormpath.resources.group.Group` objects.
            - Group hrefs, ex:
                'https://api.stormpath.com/v1/groups/3wzkqr03K8WxRp8NQuYSs3'
            - Group names, ex: 'admins'.
            - A search query, ex: {'name': '*_admins'}.

                This could look something like:

                [
                    group,
                    'https://api.stormpath.com/v1/groups/3wzkqr03K8WxRp8NQuYSs3',
                    'admins',
                    {'name': '*_admins'},
                ]

        .. note::
            Passing in a :class:`stormpath.resources.group.Group` object will
            always be the quickest way to add a Group, as it doesn't require
            any additional API calls.
        """
        for g in [self._resolve_group(group) for group in resolvables]:
            self._client.group_memberships.create({
                'account': self,
                'group': g,
            })

    def has_group(self, resolvable):
        """Check to see whether or not this Account is a member of the
        specified Group.

        :param resolvable: This could be any one of the following:

            - A :class:`stormpath.resources.group.Group` object.
            - A Group href, ex:
                'https://api.stormpath.com/v1/groups/3wzkqr03K8WxRp8NQuYSs3'
            - A Group name, ex: 'admins'.
            - A search query, ex: {'name': '*_admins'}.

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
            - A search query, ex: {'name': '*_admins'}.

                This could look something like:

                [
                    group,
                    'https://api.stormpath.com/v1/groups/3wzkqr03K8WxRp8NQuYSs3',
                    'admins',
                    {'name': '*_admins'},
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
            - A search query, ex: {'name': '*_admins'}.

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

    def remove_groups(self, resolvables):
        """Remove this Account from the specified Groups.

        :param resolvables: A list of either:

            - A :class:`stormpath.resources.group.Group` object.
            - A Group href, ex:
                'https://api.stormpath.com/v1/groups/3wzkqr03K8WxRp8NQuYSs3'
            - A Group name, ex: 'admins'.
            - A search query, ex: {'name': '*_admins'}.

        :raises: :class:`stormpath.error.StormpathError` if the Groups
            specified do not contain this Account.

        .. note::
            Passing in a :class:`stormpath.resources.group.Group` object will
            always be the quickest way to check a Group's membership, since it
            doesn't require any additional API calls.
        """
        memberships = [membership for membership in self.group_memberships]
        for g in [self._resolve_group(group) for group in resolvables]:
            done = False
            for membership in memberships:
                if membership.group.href == g.href:
                    membership.delete()
                    done = True

            if not done:
                raise StormpathError({
                    'developerMessage': 'This user is not part of Group %s.' % g.name,
                })


# Proxy methods for convenience.
Account.in_group = Account.has_group
Account.in_groups = Account.has_groups


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

    def create(self, properties, expand=None, password_format=None, **params):
        """If password_format is specified, account will be created
        using existing password hash.

        http://docs.stormpath.com/python/product-guide/#create-an-account-with-an-existing-password-hash
        """
        data, params = self._prepare_for_create(properties, expand, **params)

        create_path = self._get_create_path()
        if password_format:
            create_path += '?passwordFormat=' + password_format

        created = self.resource_class(
            self._client,
            properties=self._store.create_resource(
                create_path,
                data,
                params=params
            )
        )

        dispatcher.send(
            signal=SIGNAL_RESOURCE_CREATED, sender=self.resource_class,
            data=data, params=params)

        return created

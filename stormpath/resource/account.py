from .base import Resource, ResourceList, StatusMixin
from ..error import Error


class Account(Resource, StatusMixin):
    readwrite_attrs = ('username', 'password', 'email', 'given_name',
        'middle_name', 'surname', 'status', 'email_verification_token')

    def get_resource_attributes(self):
        from .directory import Directory
        from .group import GroupList
        from .group_membership import GroupMembershipList
        return {
            'directory': Directory,
            'groups': GroupList,
            'group_memberships': GroupMembershipList,
            'email_verification_token': Resource
        }

    def __str__(self):
        return self.username

    def add_group(self, group):
        return self._client.group_memberships.create({
            'account': self,
            'group': group
        })

    def verify_email_token(self, token):
        href = '/accounts/emailVerificationTokens/' + token
        try:
            data = self._store.create_resource(href, {})
        except Error as e:
            if e.code == 404:
                return None
            else:
                raise
        return self.__class__(properties=data, client=self._client)

class AccountList(ResourceList):
    resource_class = Account


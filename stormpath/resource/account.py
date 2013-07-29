from .base import Resource, ResourceList, StatusMixin


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
        self._client.group_memberships.create({
            'account': self,
            'group': group
        })


class AccountList(ResourceList):
    resource_class = Account

    def verify_email_token(self, token):
        href = '/accounts/emailVerificationTokens/' + token
        self._store.create_resource(href, {})

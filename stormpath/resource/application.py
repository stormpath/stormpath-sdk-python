"""Stormpath Application resource mappings."""


from .base import (
    CollectionResource,
    DeleteMixin,
    Resource,
    SaveMixin,
    StatusMixin,
)
from .login_attempt import LoginAttemptList
from .password_reset_token import PasswordResetTokenList


class Application(DeleteMixin, Resource, SaveMixin, StatusMixin):
    """Stormpath Application resource.

    More info in documentation:
    http://docs.stormpath.com/python/product-guide/#applications
    """
    writable_attrs = (
        'description',
        'name',
        'status',
    )

    def get_resource_attributes(self):
        from .account import AccountList
        from .account_store_mapping import (
            AccountStoreMapping,
            AccountStoreMappingList,
        )
        from .group import GroupList
        from .tenant import Tenant

        return {
            'accounts': AccountList,
            'account_store_mappings': AccountStoreMappingList,
            'default_account_store_mapping': AccountStoreMapping,
            'default_group_store_mapping': AccountStoreMapping,
            'groups': GroupList,
            'login_attempts': LoginAttemptList,
            'password_reset_tokens': PasswordResetTokenList,
            'tenant': Tenant,
        }

    def authenticate_account(self, login, password):
        """Authenticate an Account against this Application.

        :param login: Username or email address.
        :param password: Unencrypted user password.
        """
        return self.login_attempts.basic_auth(login, password).account

    def send_password_reset_email(self, email):
        """Send a password reset email.

        More info in documentation:
        http://docs.stormpath.com/rest/product-guide/#reset-an-accounts-password

        :param email: Email address to send the email to.
        """
        token = self.password_reset_tokens.create({'email': email})
        return token.account

    def verify_password_reset_token(self, token):
        """Verify password reset by using a token.

        :param token: password reset token extracted from the URL.
        """
        return self.password_reset_tokens[token].account


class ApplicationList(CollectionResource):
    """Application resource list.
    """
    create_path = '/applications'
    resource_class = Application

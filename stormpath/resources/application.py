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


class Application(Resource, DeleteMixin, SaveMixin, StatusMixin):
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

    def authenticate_account(self, login, password, expand=None,
            account_store=None):
        """Authenticate Account inside the Application.

        :param login: Username or email address

        :param password: Unencrypted user password

        :param expand:
            A :class:`stormpath.resources.base.Expansion` object (optional)

        :param account_store:
            A specific :class:`stormpath.resources.account_store.AccountStore`
            object to authenticate against (optional)
        """
        return self.login_attempts.basic_auth(login, password, expand,
            account_store)

    def get_provider_account(self, provider, **provider_kwargs):
        """Used for getting account data from 3rd party Providers
        (ie. Google, Facebook)

        :param provider: Can be one of the following Constants:

            * :const:`stormpath.resources.provider.Provider.GOOGLE`

            * :const:`stormpath.resources.provider.Provider.FACEBOOK`

            * :const:`stormpath.resources.provider.Provider.STORMPATH`


        :param provider_kwargs: Which specific kwargs are needed depends on the chosen Provider.

            {
                'code': '...',

                'access_token': '...',

                'client_id': '...',

                'client_secret': '...'
            }



        """
        provider_data = provider_kwargs.copy()
        provider_data['provider_id'] = provider

        return self.accounts.create({
            'provider_data': provider_data
        })

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
    """Application resource list."""
    create_path = '/applications'
    resource_class = Application

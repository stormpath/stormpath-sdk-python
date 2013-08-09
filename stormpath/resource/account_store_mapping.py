from .base import Resource, ResourceList
from ..error import Error


class AccountStoreMapping(Resource):
    """Mapping between an Application and an account store.

    Account Store is a generic term for a resource that stores Accounts.
    Currently, this includes Directories and Groups.

    More info in documentation:
    https://www.stormpath.com/docs/python/product-guide#ManageAccountStores
    """

    writable_attrs = ('application', 'account_store', 'list_index',
        'is_default_account_store', 'is_default_group_store')

    def get_resource_attributes(self):
        from .application import Application
        from .account_store import AccountStore

        return {
            'application': Application,
            'account_store': AccountStore,
        }

    def authenticate_account(self, login, password):
        try:
            return self.login_attempts.basic_auth(login, password).account
        except Error as e:
            if e.status_code == 400:
                return None
            else:
                raise

    def send_password_reset_email(self, email):
        token = self.password_reset_tokens.create({'email': email})
        return token.account

    def verify_password_reset_token(self, token):
        try:
            return self.password_reset_tokens[token].account
        except Error as e:
            if e.status_code == 404:
                return None
            else:
                raise


class AccountStoreMappingList(ResourceList):
    """Account Store Mapping list."""

    create_path = '/accountStoreMappings'
    resource_class = AccountStoreMapping

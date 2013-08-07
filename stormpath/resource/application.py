'''Application resource.

More info in documentation:
https://www.stormpath.com/docs/python/product-guide#Applications
'''


from .base import Resource, ResourceList, StatusMixin
from .password_reset_token import PasswordResetTokenList
from .login_attempt import LoginAttemptList
from ..error import Error


class Application(Resource, StatusMixin):

    writable_attrs = ('name', 'description', 'status')

    def get_resource_attributes(self):
        from .tenant import Tenant
        from .account import AccountList
        from .group import GroupList
        return {
            'tenant': Tenant,
            'accounts': AccountList,
            'groups': GroupList,
            'password_reset_tokens': PasswordResetTokenList,
            'login_attempts': LoginAttemptList,
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


class ApplicationList(ResourceList):
    create_path = '/applications'
    resource_class = Application

from base64 import b64encode
from .base import Resource, CollectionResource


class LoginAttempt(Resource):
    """Handles Base64-encoded login data.

    More info in documentation:
    https://www.stormpath.com/docs/rest/product-guide#AuthenticateAccounts
    """

    writable_attrs = ('type', 'value')

    def get_resource_attributes(self):
        from .account import Account
        return {
            'account': Account
        }


class LoginAttemptList(CollectionResource):
    """List of login data.
    """
    resource_class = LoginAttempt

    def basic_auth(self, login, password, expand):
        value = login + ':' + password
        value = b64encode(value.encode('utf-8')).decode('ascii')
        return self.create({
            'type': 'basic',
            'value': value,
        }, expand=expand)

"""Stormpath LoginAttempt resource mappings."""


from base64 import b64encode

from .base import (
    CollectionResource,
    Resource,
)


class LoginAttempt(Resource):
    """Handles Base64-encoded login data.

    More info in documentation:
    http://docs.stormpath.com/rest/product-guide/#authenticate-an-account
    """
    writable_attrs = (
        'type',
        'value',
    )

    def get_resource_attributes(self):
        from .account import Account
        return {
            'account': Account
        }


class LoginAttemptList(CollectionResource):
    """List of login data.
    """
    resource_class = LoginAttempt

    def basic_auth(self, login, password):
        value = login + ':' + password
        value = b64encode(value.encode('utf-8')).decode('ascii')
        return self.create({
            'type': 'basic',
            'value': value
        })

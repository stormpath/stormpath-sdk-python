"""Stormpath LoginAttempt resource mappings."""


import datetime
import jwt
from base64 import b64encode
from oauthlib.common import to_unicode
from stormpath.api_auth import AccessToken
from uuid import uuid4

from .base import (
    CollectionResource,
    Resource,
)


class AuthenticationResult(Resource):
    """Handles Base64-encoded login data.

    More info in documentation:
    http://docs.stormpath.com/rest/product-guide/#authenticate-an-account
    """

    writable_attrs = ('type', 'value', 'account_store', 'application')

    @staticmethod
    def get_resource_attributes():
        from .account import Account

        return {
            'account': Account,
        }

    def __repr__(self):
        return '<%s attributes=%s>' % (self.__class__.__name__,
            str(self._get_property_names()))

    def get_jwt(self):
        if not hasattr(self, 'application'):
            raise ValueError('JWT cannot be generated without application')

        secret = self.application._client.auth.secret
        now = datetime.datetime.utcnow()

        try:
            jti = uuid4().get_hex()
        except AttributeError:
            jti = uuid4().hex

        data = {
            'iss': self.application.href,
            'sub': self.account.href,
            'jti': jti,
            'exp': now + datetime.timedelta(seconds=3600)
        }

        token = jwt.encode(data, secret, 'HS256')
        token = to_unicode(token, 'UTF-8')

        return token

    def get_access_token(self, jwt=None):
        if not hasattr(self, 'application'):
            raise ValueError(
                'Access token cannot be generated without application')

        if jwt is None:
            jwt = self.get_jwt()

        return AccessToken(self.application, jwt)

    def get_access_token_response(self, jwt=None):
        return self.get_access_token(jwt).to_json()


class LoginAttemptList(CollectionResource):
    """List of login data."""
    resource_class = AuthenticationResult

    def basic_auth(self, login, password, expand, account_store=None,
                   app=None, organization_name_key=None):
        value = login + ':' + password
        value = b64encode(value.encode('utf-8')).decode('ascii')
        properties = {
            'type': 'basic',
            'value': value,
        }

        if account_store:
            properties['account_store'] = account_store
        if organization_name_key:
            properties['account_store'] = {
                'name_key': organization_name_key
            }

        result = self.create(properties, expand=expand)

        if app:
            result.application = app

        return result

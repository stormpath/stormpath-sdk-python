import base64
from collections import OrderedDict

import jwt
from unittest import TestCase
from six import u
try:
    from mock import patch, MagicMock
except ImportError:
    from unittest.mock import patch, MagicMock

from stormpath.api_auth import *
from stormpath.client import Client
from stormpath.error import Error as StormpathError
from stormpath.resources import Account
from stormpath.resources.base import StatusMixin

FAKE_CLIENT_ID = 'fake_client_id'
FAKE_CLIENT_SECRET = 'fake_client_secret'


class ApiRequestAuthenticatorTest(TestCase):

    def test_basic_api_auth(self):
        app = MagicMock()
        app._client.auth.secret = 'fakeApiKeyProperties.secret'
        app.href = 'HREF'
        api_keys = MagicMock()
        api_keys.get_key = lambda k, s=None: MagicMock(id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET, status=StatusMixin.STATUS_ENABLED)
        app.api_keys = api_keys

        basic_auth = base64.b64encode("{}:{}".format(FAKE_CLIENT_ID, FAKE_CLIENT_SECRET).encode('utf-8'))

        uri = 'https://example.com/get'
        http_method = 'GET'
        body = {}
        headers = {'Authorization': b'Basic ' + basic_auth}
        allowed_scopes = ['test1']

        authenticator = ApiRequestAuthenticator(app)
        result = authenticator.authenticate(headers=headers, http_method=http_method, uri=uri, body=body, scopes=allowed_scopes)

        self.assertIsNotNone(result)
        self.assertIsNone(result.token)
        self.assertIsNotNone(result.api_key)

    def test_basic_api_auth_unicode(self):
        app = MagicMock()
        app._client.auth.secret = 'fakeApiKeyProperties.secret'
        app.href = 'HREF'
        api_keys = MagicMock()
        api_keys.get_key = lambda k, s=None: MagicMock(id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET, status=StatusMixin.STATUS_ENABLED)
        app.api_keys = api_keys

        basic_auth = base64.b64encode('{}:{}'.format(FAKE_CLIENT_ID, FAKE_CLIENT_SECRET).encode('utf-8'))
        uri = 'https://example.com/get'
        http_method = 'GET'
        body = {}
        headers = {'Authorization': u('Basic ') + basic_auth.decode('utf-8')}
        allowed_scopes = ['test1']

        authenticator = ApiRequestAuthenticator(app)
        result = authenticator.authenticate(headers=headers, http_method=http_method, uri=uri, body=body, scopes=allowed_scopes)

        self.assertIsNotNone(result)
        self.assertIsNone(result.token)
        self.assertIsNotNone(result.api_key)

    def test_basic_api_auth_with_generating_bearer_token(self):
        app = MagicMock()
        app._client.auth.secret = 'fakeApiKeyProperties.secret'
        app.href = 'HREF'
        api_keys = MagicMock()
        api_keys.get_key = lambda k, s=None: MagicMock(id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET, status=StatusMixin.STATUS_ENABLED)
        app.api_keys = api_keys
        basic_auth = base64.b64encode("{}:{}".format(FAKE_CLIENT_ID, FAKE_CLIENT_SECRET).encode('utf-8'))
        uri = 'https://example.com/get'
        http_method = 'GET'
        body = {'grant_type': 'client_credentials', 'scope': 'test1'}
        headers = {'Authorization': b'Basic ' + basic_auth}
        allowed_scopes = ['test1']

        authenticator = ApiRequestAuthenticator(app)
        result = authenticator.authenticate(headers=headers, http_method=http_method, uri=uri, body=body, scopes=allowed_scopes)

        self.assertIsNotNone(result)
        self.assertIsNotNone(result.api_key)
        self.assertIsNotNone(result.token)
        self.assertEquals(result.token.scopes, ['test1'])

    def test_basic_api_auth_with_invalid_scope_no_token_get_generated(self):
        app = MagicMock()
        app._client.auth.secret = 'fakeApiKeyProperties.secret'
        app.href = 'HREF'
        api_keys = MagicMock()
        api_keys.get_key = lambda k, s=None: MagicMock(id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET, status=StatusMixin.STATUS_ENABLED)
        app.api_keys = api_keys
        basic_auth = base64.b64encode("{}:{}".format(FAKE_CLIENT_ID, FAKE_CLIENT_SECRET).encode('utf-8'))
        uri = 'https://example.com/get'
        http_method = 'GET'
        body = {'grant_type': 'client_credentials', 'scope': 'invalid_scope'}
        headers = {'Authorization': b'Basic ' + basic_auth}
        allowed_scopes = ['test1']
        authenticator = ApiRequestAuthenticator(app)
        result = authenticator.authenticate(headers=headers, http_method=http_method, uri=uri, body=body, scopes=allowed_scopes)

        self.assertIsNotNone(result)
        self.assertIsNone(result.token)

    def test_basic_api_auth_invalid_credentials(self):
        app = MagicMock()
        app._client.auth.secret = 'fakeApiKeyProperties.secret'
        app.href = 'HREF'
        api_keys = MagicMock()
        api_keys.get_key = lambda k, s=None: None
        app.api_keys = api_keys
        basic_auth = base64.b64encode("invalid_client_id:invalid_client_secret".encode('utf-8'))
        uri = 'https://example.com/get'
        http_method = 'GET'
        # body = {}
        body = {'grant_type': 'client_credentials', 'scope': 'test1'}
        headers = {'Authorization': b'Basic ' + basic_auth}
        allowed_scopes = ['test1']

        authenticator = ApiRequestAuthenticator(app)
        result = authenticator.authenticate(headers=headers, http_method=http_method, uri=uri, body=body, scopes=allowed_scopes)

        self.assertIsNone(result)

    def test_bearer_api_auth(self):
        app = MagicMock()
        app._client.auth.secret = 'fakeApiKeyProperties.secret'
        app.href = 'HREF'
        api_keys = MagicMock()
        api_keys.get_key = lambda k, s=None: MagicMock(id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET, status=StatusMixin.STATUS_ENABLED)
        app.api_keys = api_keys
        basic_auth = base64.b64encode("{}:{}".format(FAKE_CLIENT_ID, FAKE_CLIENT_SECRET).encode('utf-8'))
        uri = 'https://example.com/get'
        http_method = 'GET'
        body = {'grant_type': 'client_credentials', 'scope': 'test1'}
        headers = {'Authorization': b'Basic ' + basic_auth}
        allowed_scopes = ['test1']

        authenticator = ApiRequestAuthenticator(app)
        result = authenticator.authenticate(headers=headers, http_method=http_method, uri=uri, body=body, scopes=allowed_scopes)

        self.assertIsNotNone(result)
        self.assertIsNotNone(result.token)
        token = result.token
        body = {}
        headers = {'Authorization': b'Bearer ' + token.token.encode('utf-8')}

        result = authenticator.authenticate(headers=headers, http_method=http_method, uri=uri, body=body, scopes=allowed_scopes)

        self.assertIsNotNone(result)
        self.assertEquals(result.token.token, token.token)

    def test_bearer_api_auth_with_unicode(self):
        app = MagicMock()
        app._client.auth.secret = 'fakeApiKeyProperties.secret'
        app.href = 'HREF'
        api_keys = MagicMock()
        api_keys.get_key = lambda k, s=None: MagicMock(id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET, status=StatusMixin.STATUS_ENABLED)
        app.api_keys = api_keys
        basic_auth = base64.b64encode('{}:{}'.format(FAKE_CLIENT_ID, FAKE_CLIENT_SECRET).encode('utf-8'))
        uri = 'https://example.com/get'
        http_method = 'GET'
        body = {'grant_type': 'client_credentials', 'scope': 'test1'}
        headers = {'Authorization': u('Basic ') + basic_auth.decode('utf-8')}
        allowed_scopes = ['test1']

        authenticator = ApiRequestAuthenticator(app)
        result = authenticator.authenticate(headers=headers, http_method=http_method, uri=uri, body=body, scopes=allowed_scopes)

        self.assertIsNotNone(result)
        self.assertIsNotNone(result.token)
        token = result.token
        body = {}
        headers = {'Authorization': b'Bearer ' + token.token.encode('utf-8')}

        result = authenticator.authenticate(headers=headers, http_method=http_method, uri=uri, body=body, scopes=allowed_scopes)

        self.assertIsNotNone(result)
        self.assertEquals(result.token.token, token.token)

    def test_bearer_api_auth_with_token_in_url(self):
        app = MagicMock()
        app._client.auth.secret = 'fakeApiKeyProperties.secret'
        app.href = 'HREF'
        api_keys = MagicMock()
        api_keys.get_key = lambda k, s=None: MagicMock(id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET, status=StatusMixin.STATUS_ENABLED)
        app.api_keys = api_keys
        basic_auth = base64.b64encode('{}:{}'.format(FAKE_CLIENT_ID, FAKE_CLIENT_SECRET).encode('utf-8'))
        body = {'grant_type': 'client_credentials', 'scope': 'test1'}
        headers = {'Authorization': b'Basic ' + basic_auth}
        allowed_scopes = ['test1']

        authenticator = ApiRequestAuthenticator(app)
        result = authenticator.authenticate(headers=headers, body=body, scopes=allowed_scopes)

        self.assertIsNotNone(result)
        self.assertIsNotNone(result.token)
        token = result.token
        uri = 'https://example.com/get?access_token=%s' % (token.token)
        result = authenticator.authenticate(headers={}, uri=uri, body=body, scopes=allowed_scopes)

        self.assertIsNotNone(result)
        self.assertEquals(result.token.token, token.token)

    def test_bearer_api_auth_with_token_in_body(self):
        app = MagicMock()
        app._client.auth.secret = 'fakeApiKeyProperties.secret'
        app.href = 'HREF'
        api_keys = MagicMock()
        api_keys.get_key = lambda k, s=None: MagicMock(id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET, status=StatusMixin.STATUS_ENABLED)
        app.api_keys = api_keys
        basic_auth = base64.b64encode('{}:{}'.format(FAKE_CLIENT_ID, FAKE_CLIENT_SECRET).encode('utf-8'))
        body = {'grant_type': 'client_credentials', 'scope': 'test1'}
        headers = {'Authorization': b'Basic ' + basic_auth}
        allowed_scopes = ['test1']

        authenticator = ApiRequestAuthenticator(app)
        result = authenticator.authenticate(headers=headers, body=body, scopes=allowed_scopes)

        self.assertIsNotNone(result)
        self.assertIsNotNone(result.token)
        token = result.token
        body = {'access_token': token.token}

        authenticator = ApiRequestAuthenticator(app)
        result = authenticator.authenticate(headers={}, body=body, scopes=allowed_scopes)

        self.assertIsNotNone(result)
        self.assertEquals(result.token.token, token.token)

    def test_bearer_api_auth_with_token_in_body_without_locations(self):
        app = MagicMock()
        app._client.auth.secret = 'fakeApiKeyProperties.secret'
        app.href = 'HREF'
        api_keys = MagicMock()
        api_keys.get_key = lambda k, s=None: MagicMock(id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET, status=StatusMixin.STATUS_ENABLED)
        app.api_keys = api_keys
        basic_auth = base64.b64encode('{}:{}'.format(FAKE_CLIENT_ID, FAKE_CLIENT_SECRET).encode('utf-8'))
        body = {'grant_type': 'client_credentials', 'scope': 'test1'}
        headers = {'Authorization': b'Basic ' + basic_auth}
        allowed_scopes = ['test1']

        authenticator = ApiRequestAuthenticator(app)
        result = authenticator.authenticate(headers=headers, body=body, scopes=allowed_scopes)

        self.assertIsNotNone(result)
        self.assertIsNotNone(result.token)
        token = result.token
        body = {'access_token': token.token}
        result = authenticator.authenticate(headers={}, body=body, scopes=allowed_scopes)

        self.assertIsNotNone(result)
        self.assertEquals(result.token.token, token.token)

    def test_access_token_validity_expired_token(self):
        app = MagicMock()
        app._client.auth.secret = 'fakeApiKeyProperties.secret'
        app.href = 'HREF'
        api_keys = MagicMock()
        api_keys.get_key = lambda k, s=None: MagicMock(id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET, status=StatusMixin.STATUS_ENABLED)
        app.api_keys = api_keys

        access_token = AccessToken(app=app, token='eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJIUkVGIiwiaWF0IjoxNDA1NDI5MDU5LCJleHAiOjE0MDU0MzI2NTksInN1YiI6ImZha2VfY2xpZW50X2lkIiwic2NvcGUiOiJ0ZXN0MSJ9.dNPzOg8cFxkknakTAccRfcGoRiPjn7z-M5TUacy5OTE')
        self.assertFalse(access_token._is_valid())

    def test_access_token_scope_check(self):
        app = MagicMock()
        app._client.auth.secret = 'fakeApiKeyProperties.secret'
        app.href = 'HREF'
        api_keys = MagicMock()
        api_keys.get_key = lambda k, s=None: MagicMock(id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET, status=StatusMixin.STATUS_ENABLED)
        app.api_keys = api_keys

        access_token = AccessToken(app=app, token='eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJIUkVGIiwiaWF0IjoxNDA1NDI5MDU5LCJleHAiOjE0MDU0MzI2NTksInN1YiI6ImZha2VfY2xpZW50X2lkIiwic2NvcGUiOiJ0ZXN0MSJ9.dNPzOg8cFxkknakTAccRfcGoRiPjn7z-M5TUacy5OTE')
        self.assertFalse(access_token._within_scope(['fake_scope_that_the_token_doesnt_have']))

    def test_access_token_invalid_token(self):
        app = MagicMock()
        app._client.auth.secret = 'fakeApiKeyProperties.secret'
        app.href = 'HREF'
        api_keys = MagicMock()
        api_keys.get_key = lambda k, s=None: MagicMock(id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET, status=StatusMixin.STATUS_ENABLED)
        app.api_keys = api_keys

        access_token = AccessToken(app=app, token='invalid_token_format')
        self.assertFalse(access_token._is_valid())

    def test_access_token_with_minor_clock_skew(self):
        app = MagicMock()
        app._client.auth.secret = 'fakeApiKeyProperties.secret'
        app.href = 'HREF'
        api_keys = MagicMock()
        api_keys.get_key = lambda k, s=None: MagicMock(id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET, status=StatusMixin.STATUS_ENABLED)
        app.api_keys = api_keys
        now = datetime.datetime.utcnow()
        fake_jwt_data = {
            'iss': 'HREF',
            'iat': now + datetime.timedelta(seconds=2),
            'exp': now + datetime.timedelta(seconds=3600),
            'sub': 'fake_client_id',
            'scope': 'test1',
        }
        fake_jwt = to_unicode(jwt.encode(fake_jwt_data, app._client.auth.secret, 'HS256'), 'UTF-8')

        access_token = AccessToken(app=app, token=fake_jwt)
        self.assertTrue(access_token._is_valid())

    def test_access_token_with_major_clock_skew(self):
        app = MagicMock()
        app._client.auth.secret = 'fakeApiKeyProperties.secret'
        app.href = 'HREF'
        api_keys = MagicMock()
        api_keys.get_key = lambda k, s=None: MagicMock(id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET, status=StatusMixin.STATUS_ENABLED)
        app.api_keys = api_keys
        now = datetime.datetime.utcnow()
        fake_jwt_data = {
            'iss': 'HREF',
            'iat': now + datetime.timedelta(seconds=20),
            'exp': now + datetime.timedelta(seconds=3600),
            'sub': 'fake_client_id',
            'scope': 'test1',
        }
        fake_jwt = to_unicode(jwt.encode(fake_jwt_data, app._client.auth.secret, 'HS256'), 'UTF-8')
        access_token = AccessToken(app=app, token=fake_jwt)

        with self.assertRaises(jwt.InvalidIssuedAtError):
            access_token._is_valid()

    def test_valid_bearer_token_but_deleted_api_key(self):
        app = MagicMock()
        app._client.auth.secret = 'fakeApiKeyProperties.secret'
        app.href = 'HREF'
        api_keys = MagicMock()
        api_keys.get_key = lambda k, s=None: MagicMock(id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET, status=StatusMixin.STATUS_ENABLED)
        app.api_keys = api_keys
        ds = MagicMock()
        ds.get_resource.side_effect = StormpathError({'developerMessage': 'No username on account.'})
        client = MagicMock(data_store=ds)
        app.accounts.get.return_value = Account(client=client, href='account')
        basic_auth = base64.b64encode('{}:{}'.format(FAKE_CLIENT_ID, FAKE_CLIENT_SECRET).encode('utf-8'))
        uri = 'https://example.com/get'
        http_method = 'GET'
        body = {'grant_type': 'client_credentials', 'scope': 'test1'}
        headers = {'Authorization': b'Basic ' + basic_auth}
        allowed_scopes = ['test1']

        authenticator = ApiRequestAuthenticator(app)
        result = authenticator.authenticate(headers=headers, http_method=http_method, uri=uri, body=body, scopes=allowed_scopes)

        self.assertIsNotNone(result)
        self.assertIsNotNone(result.token)

        token = result.token
        body = {}
        headers = {'Authorization': b'Bearer ' + token.token.encode('utf-8')}
        api_keys.get_key = lambda k, s=None: None

        result = authenticator.authenticate(headers=headers, http_method=http_method, uri=uri, body=body, scopes=allowed_scopes)
        self.assertIsNone(result)

    def test_valid_bearer_token_but_disabled_api_key(self):
        app = MagicMock()
        app._client.auth.secret = 'fakeApiKeyProperties.secret'
        app.href = 'HREF'
        api_keys = MagicMock()
        api_keys.get_key = lambda k, s=None: MagicMock(id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET, status=StatusMixin.STATUS_ENABLED)
        app.api_keys = api_keys
        api_keys.get_key = lambda k, s=None: MagicMock(id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET, status=StatusMixin.STATUS_ENABLED)
        app.api_keys = api_keys
        ds = MagicMock()
        ds.get_resource.side_effect = StormpathError({'developerMessage': 'No username on account.'})
        client = MagicMock(data_store=ds)
        app.accounts.get.return_value = Account(client=client, href='account')
        basic_auth = base64.b64encode('{}:{}'.format(FAKE_CLIENT_ID, FAKE_CLIENT_SECRET).encode('utf-8'))
        uri = 'https://example.com/get'
        http_method = 'GET'
        body = {'grant_type': 'client_credentials', 'scope': 'test1'}
        headers = {'Authorization': b'Basic ' + basic_auth}
        allowed_scopes = ['test1']

        authenticator = ApiRequestAuthenticator(app)
        result = authenticator.authenticate(headers=headers, http_method=http_method, uri=uri, body=body, scopes=allowed_scopes)

        self.assertIsNotNone(result)
        self.assertIsNotNone(result.token)

        token = result.token
        body = {}
        headers = {'Authorization': b'Bearer ' + token.token.encode('utf-8')}
        disabled_api_key = MagicMock(id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET, status=StatusMixin.STATUS_DISABLED)
        disabled_api_key.is_enabled.return_value = False
        api_keys.get_key = lambda k, s=None: disabled_api_key

        result = authenticator.authenticate(headers=headers, http_method=http_method, uri=uri, body=body, scopes=allowed_scopes)
        self.assertIsNone(result)

    def test_invalid_grant_type_no_token_gets_generated(self):
        app = MagicMock()
        app._client.auth.secret = 'fakeApiKeyProperties.secret'
        app.href = 'HREF'
        api_keys = MagicMock()
        api_keys.get_key = lambda k, s=None: MagicMock(id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET, status=StatusMixin.STATUS_ENABLED)
        app.api_keys = api_keys

        basic_auth = base64.b64encode('{}:{}'.format(FAKE_CLIENT_ID, FAKE_CLIENT_SECRET).encode('utf-8'))

        uri = 'https://example.com/get'
        http_method = 'GET'
        body = {'grant_type': 'invalid_grant', 'scope': 'test1'}
        headers = {'Authorization': b'Basic ' + basic_auth}
        allowed_scopes = ['test1']

        authenticator = ApiRequestAuthenticator(app)
        result = authenticator.authenticate(headers=headers, http_method=http_method, uri=uri, body=body, scopes=allowed_scopes)

        self.assertIsNotNone(result)
        self.assertIsNone(result.token)


class BasicRequestAuthenticatorTest(TestCase):

    def test_basic_api_auth(self):
        app = MagicMock()
        app._client.auth.secret = 'fakeApiKeyProperties.secret'
        app.href = 'HREF'
        api_keys = MagicMock()
        api_keys.get_key = lambda k, s=None: MagicMock(id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET, status=StatusMixin.STATUS_ENABLED)
        app.api_keys = api_keys
        basic_auth = base64.b64encode('{}:{}'.format(FAKE_CLIENT_ID, FAKE_CLIENT_SECRET).encode('utf-8'))
        uri = 'https://example.com/get'
        http_method = 'GET'
        body = {}
        headers = {'Authorization': b'Basic ' + basic_auth}
        allowed_scopes = ['test1']

        authenticator = BasicRequestAuthenticator(app)
        result = authenticator.authenticate(headers=headers, http_method=http_method, uri=uri, body=body, scopes=allowed_scopes)

        self.assertIsNotNone(result)
        self.assertIsNone(result.token)
        self.assertIsNotNone(result.api_key)

    def test_basic_api_auth_unicode(self):
        app = MagicMock()
        app._client.auth.secret = 'fakeApiKeyProperties.secret'
        app.href = 'HREF'
        api_keys = MagicMock()
        api_keys.get_key = lambda k, s=None: MagicMock(id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET, status=StatusMixin.STATUS_ENABLED)
        app.api_keys = api_keys
        basic_auth = base64.b64encode('{}:{}'.format(FAKE_CLIENT_ID, FAKE_CLIENT_SECRET).encode('utf-8'))
        uri = 'https://example.com/get'
        http_method = 'GET'
        body = {}
        headers = {'Authorization': u('Basic ') + basic_auth.decode('utf-8')}
        allowed_scopes = ['test1']

        authenticator = BasicRequestAuthenticator(app)
        result = authenticator.authenticate(headers=headers, http_method=http_method, uri=uri, body=body, scopes=allowed_scopes)

        self.assertIsNotNone(result)
        self.assertIsNone(result.token)
        self.assertIsNotNone(result.api_key)

    def test_basic_api_auth_doesnt_generate_bearer_token(self):
        app = MagicMock()
        app._client.auth.secret = 'fakeApiKeyProperties.secret'
        app.href = 'HREF'
        api_keys = MagicMock()
        api_keys.get_key = lambda k, s=None: MagicMock(id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET, status=StatusMixin.STATUS_ENABLED)
        app.api_keys = api_keys
        basic_auth = base64.b64encode('{}:{}'.format(FAKE_CLIENT_ID, FAKE_CLIENT_SECRET).encode('utf-8'))
        uri = 'https://example.com/get'
        http_method = 'GET'
        body = {'grant_type': 'client_credentials', 'scope': 'test1'}
        headers = {'Authorization': b'Basic ' + basic_auth}
        allowed_scopes = ['test1']

        authenticator = BasicRequestAuthenticator(app)
        result = authenticator.authenticate(headers=headers, http_method=http_method, uri=uri, body=body, scopes=allowed_scopes)

        self.assertIsNotNone(result)
        self.assertIsNotNone(result.api_key)
        self.assertIsNone(result.token)

    def test_basic_api_auth_with_invalid_scope_no_token_get_generated(self):
        app = MagicMock()
        app._client.auth.secret = 'fakeApiKeyProperties.secret'
        app.href = 'HREF'
        api_keys = MagicMock()
        api_keys.get_key = lambda k, s=None: MagicMock(id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET, status=StatusMixin.STATUS_ENABLED)
        app.api_keys = api_keys
        basic_auth = base64.b64encode('{}:{}'.format(FAKE_CLIENT_ID, FAKE_CLIENT_SECRET).encode('utf-8'))
        uri = 'https://example.com/get'
        http_method = 'GET'
        body = {'grant_type': 'client_credentials', 'scope': 'invalid_scope'}
        headers = {'Authorization': b'Basic ' + basic_auth}
        allowed_scopes = ['test1']

        authenticator = BasicRequestAuthenticator(app)
        result = authenticator.authenticate(headers=headers, http_method=http_method, uri=uri, body=body, scopes=allowed_scopes)

        self.assertIsNotNone(result)
        self.assertIsNone(result.token)

    def test_basic_api_auth_invalid_credentials(self):
        app = MagicMock()
        app._client.auth.secret = 'fakeApiKeyProperties.secret'
        app.href = 'HREF'
        api_keys = MagicMock()
        api_keys.get_key = lambda k, s=None: None
        app.api_keys = api_keys
        basic_auth = base64.b64encode('invalid_client_id:invalid_client_secret'.encode('utf-8'))
        uri = 'https://example.com/get'
        http_method = 'GET'
        # body = {}
        body = {'grant_type': 'client_credentials', 'scope': 'test1'}
        headers = {'Authorization': b'Basic ' + basic_auth}
        allowed_scopes = ['test1']

        authenticator = BasicRequestAuthenticator(app)
        result = authenticator.authenticate(headers=headers, http_method=http_method, uri=uri, body=body, scopes=allowed_scopes)

        self.assertIsNone(result)


class OAuthRequestAuthenticatorTest(TestCase):

    def test_basic_api_auth_fails(self):
        app = MagicMock()
        app._client.auth.secret = 'fakeApiKeyProperties.secret'
        app.href = 'HREF'
        api_keys = MagicMock()
        api_keys.get_key = lambda k, s=None: MagicMock(id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET, status=StatusMixin.STATUS_ENABLED)
        app.api_keys = api_keys
        basic_auth = base64.b64encode('{}:{}'.format(FAKE_CLIENT_ID, FAKE_CLIENT_SECRET).encode('utf-8'))
        uri = 'https://example.com/get'
        http_method = 'GET'
        body = {}
        headers = {'Authorization': b'Basic ' + basic_auth}
        allowed_scopes = ['test1']

        authenticator = OAuthRequestAuthenticator(app)
        result = authenticator.authenticate(headers=headers, http_method=http_method, uri=uri, body=body, scopes=allowed_scopes)

        self.assertIsNone(result)

    def test_basic_api_auth_with_generating_bearer_token(self):
        app = MagicMock()
        app._client.auth.secret = 'fakeApiKeyProperties.secret'
        app.href = 'HREF'
        api_keys = MagicMock()
        api_keys.get_key = lambda k, s=None: MagicMock(id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET, status=StatusMixin.STATUS_ENABLED)
        app.api_keys = api_keys
        basic_auth = base64.b64encode('{}:{}'.format(FAKE_CLIENT_ID, FAKE_CLIENT_SECRET).encode('utf-8'))
        uri = 'https://example.com/get'
        http_method = 'GET'
        body = {'grant_type': 'client_credentials', 'scope': 'test1'}
        headers = {'Authorization': b'Basic ' + basic_auth}
        allowed_scopes = ['test1']

        authenticator = OAuthRequestAuthenticator(app)
        result = authenticator.authenticate(headers=headers, http_method=http_method, uri=uri, body=body, scopes=allowed_scopes)

        self.assertIsNotNone(result)
        self.assertIsNotNone(result.api_key)
        self.assertIsNotNone(result.token)
        self.assertEquals(result.token.scopes, ['test1'])

    def test_basic_api_auth_with_invalid_scope_no_token_get_generated(self):
        app = MagicMock()
        app._client.auth.secret = 'fakeApiKeyProperties.secret'
        app.href = 'HREF'
        api_keys = MagicMock()
        api_keys.get_key = lambda k, s=None: MagicMock(id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET, status=StatusMixin.STATUS_ENABLED)
        app.api_keys = api_keys
        basic_auth = base64.b64encode('{}:{}'.format(FAKE_CLIENT_ID, FAKE_CLIENT_SECRET).encode('utf-8'))
        uri = 'https://example.com/get'
        http_method = 'GET'
        body = {'grant_type': 'client_credentials', 'scope': 'invalid_scope'}
        headers = {'Authorization': b'Basic ' + basic_auth}
        allowed_scopes = ['test1']

        authenticator = OAuthRequestAuthenticator(app)
        result = authenticator.authenticate(headers=headers, http_method=http_method, uri=uri, body=body, scopes=allowed_scopes)

        self.assertIsNotNone(result)
        self.assertIsNone(result.token)

    def test_bearer_api_auth(self):
        app = MagicMock()
        app._client.auth.secret = 'fakeApiKeyProperties.secret'
        app.href = 'HREF'
        api_keys = MagicMock()
        api_keys.get_key = lambda k, s=None: MagicMock(id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET, status=StatusMixin.STATUS_ENABLED)
        app.api_keys = api_keys
        basic_auth = base64.b64encode('{}:{}'.format(FAKE_CLIENT_ID, FAKE_CLIENT_SECRET).encode('utf-8'))
        uri = 'https://example.com/get'
        http_method = 'GET'
        body = {'grant_type': 'client_credentials', 'scope': 'test1'}
        headers = {'Authorization': b'Basic ' + basic_auth}
        allowed_scopes = ['test1']

        authenticator = OAuthRequestAuthenticator(app)
        result = authenticator.authenticate(headers=headers, http_method=http_method, uri=uri, body=body, scopes=allowed_scopes)

        self.assertIsNotNone(result)
        self.assertIsNotNone(result.token)

        token = result.token
        body = {}
        headers = {'Authorization': b'Bearer ' + token.token.encode('utf-8')}

        result = authenticator.authenticate(headers=headers, http_method=http_method, uri=uri, body=body, scopes=allowed_scopes)

        self.assertIsNotNone(result)
        self.assertEquals(result.token.token, token.token)

    def test_bearer_api_auth_with_unicode(self):
        app = MagicMock()
        app._client.auth.secret = 'fakeApiKeyProperties.secret'
        app.href = 'HREF'
        api_keys = MagicMock()
        api_keys.get_key = lambda k, s=None: MagicMock(id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET, status=StatusMixin.STATUS_ENABLED)
        app.api_keys = api_keys
        basic_auth = base64.b64encode('{}:{}'.format(FAKE_CLIENT_ID, FAKE_CLIENT_SECRET).encode('utf-8'))
        uri = 'https://example.com/get'
        http_method = 'GET'
        body = {'grant_type': 'client_credentials', 'scope': 'test1'}
        headers = {'Authorization': u('Basic ') + basic_auth.decode('utf-8')}
        allowed_scopes = ['test1']

        authenticator = OAuthRequestAuthenticator(app)
        result = authenticator.authenticate(headers=headers, http_method=http_method, uri=uri, body=body, scopes=allowed_scopes)

        self.assertIsNotNone(result)
        self.assertIsNotNone(result.token)

        token = result.token
        body = {}
        headers = {'Authorization': b'Bearer ' + token.token.encode('utf-8')}

        result = authenticator.authenticate(headers=headers, http_method=http_method, uri=uri, body=body, scopes=allowed_scopes)

        self.assertIsNotNone(result)
        self.assertEquals(result.token.token, token.token)

    def test_bearer_api_auth_with_token_in_url(self):
        app = MagicMock()
        app._client.auth.secret = 'fakeApiKeyProperties.secret'
        app.href = 'HREF'
        api_keys = MagicMock()
        api_keys.get_key = lambda k, s=None: MagicMock(id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET, status=StatusMixin.STATUS_ENABLED)
        app.api_keys = api_keys
        basic_auth = base64.b64encode('{}:{}'.format(FAKE_CLIENT_ID, FAKE_CLIENT_SECRET).encode('utf-8'))
        body = {'grant_type': 'client_credentials', 'scope': 'test1'}
        headers = {'Authorization': b'Basic ' + basic_auth}
        allowed_scopes = ['test1']

        authenticator = OAuthRequestAuthenticator(app)
        result = authenticator.authenticate(headers=headers, body=body, scopes=allowed_scopes)

        self.assertIsNotNone(result)
        self.assertIsNotNone(result.token)

        token = result.token
        uri = 'https://example.com/get?access_token=%s' % (token.token)
        result = authenticator.authenticate(headers={}, uri=uri, body=body, scopes=allowed_scopes)

        self.assertIsNotNone(result)
        self.assertEquals(result.token.token, token.token)

    def test_bearer_api_auth_with_token_in_body(self):
        app = MagicMock()
        app._client.auth.secret = 'fakeApiKeyProperties.secret'
        app.href = 'HREF'
        api_keys = MagicMock()
        api_keys.get_key = lambda k, s=None: MagicMock(id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET, status=StatusMixin.STATUS_ENABLED)
        app.api_keys = api_keys
        basic_auth = base64.b64encode('{}:{}'.format(FAKE_CLIENT_ID, FAKE_CLIENT_SECRET).encode('utf-8'))
        body = {'grant_type': 'client_credentials', 'scope': 'test1'}
        headers = {'Authorization': b'Basic ' + basic_auth}
        allowed_scopes = ['test1']

        authenticator = OAuthRequestAuthenticator(app)
        result = authenticator.authenticate(headers=headers, body=body, scopes=allowed_scopes)

        self.assertIsNotNone(result)
        self.assertIsNotNone(result.token)

        token = result.token
        body = {'access_token': token.token}

        authenticator = OAuthRequestAuthenticator(app)
        result = authenticator.authenticate(headers={}, body=body, scopes=allowed_scopes)

        self.assertIsNotNone(result)
        self.assertEquals(result.token.token, token.token)

    def test_bearer_api_auth_with_token_in_body_without_locations(self):
        app = MagicMock()
        app._client.auth.secret = 'fakeApiKeyProperties.secret'
        app.href = 'HREF'
        api_keys = MagicMock()
        api_keys.get_key = lambda k, s=None: MagicMock(id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET, status=StatusMixin.STATUS_ENABLED)
        app.api_keys = api_keys
        basic_auth = base64.b64encode('{}:{}'.format(FAKE_CLIENT_ID, FAKE_CLIENT_SECRET).encode('utf-8'))
        body = {'grant_type': 'client_credentials', 'scope': 'test1'}
        headers = {'Authorization': b'Basic ' + basic_auth}
        allowed_scopes = ['test1']

        authenticator = OAuthRequestAuthenticator(app)
        result = authenticator.authenticate(headers=headers, body=body, scopes=allowed_scopes)

        self.assertIsNotNone(result)
        self.assertIsNotNone(result.token)

        token = result.token
        body = {'access_token': token.token}

        result = authenticator.authenticate(headers={}, body=body, scopes=allowed_scopes)

        self.assertIsNotNone(result)
        self.assertEquals(result.token.token, token.token)

    def test_valid_bearer_token_but_deleted_api_key(self):
        app = MagicMock()
        app._client.auth.secret = 'fakeApiKeyProperties.secret'
        app.href = 'HREF'
        api_keys = MagicMock()
        api_keys.get_key = lambda k, s=None: MagicMock(id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET, status=StatusMixin.STATUS_ENABLED)
        app.api_keys = api_keys
        ds = MagicMock()
        ds.get_resource.side_effect = StormpathError({'developerMessage': 'No username on account.'})
        client = MagicMock(data_store=ds)
        app.accounts.get.return_value = Account(client=client, href='account')
        basic_auth = base64.b64encode('{}:{}'.format(FAKE_CLIENT_ID, FAKE_CLIENT_SECRET).encode('utf-8'))
        uri = 'https://example.com/get'
        http_method = 'GET'
        body = {'grant_type': 'client_credentials', 'scope': 'test1'}
        headers = {'Authorization': b'Basic ' + basic_auth}
        allowed_scopes = ['test1']

        authenticator = OAuthRequestAuthenticator(app)
        result = authenticator.authenticate(headers=headers, http_method=http_method, uri=uri, body=body, scopes=allowed_scopes)

        self.assertIsNotNone(result)
        self.assertIsNotNone(result.token)

        token = result.token
        body = {}
        headers = {'Authorization': b'Bearer ' + token.token.encode('utf-8')}
        api_keys.get_key = lambda k, s=None: None

        result = authenticator.authenticate(headers=headers, http_method=http_method, uri=uri, body=body, scopes=allowed_scopes)

        self.assertIsNone(result)

    def test_valid_bearer_token_but_disabled_api_key(self):
        app = MagicMock()
        app._client.auth.secret = 'fakeApiKeyProperties.secret'
        app.href = 'HREF'
        api_keys = MagicMock()
        api_keys.get_key = lambda k, s=None: MagicMock(id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET, status=StatusMixin.STATUS_ENABLED)
        app.api_keys = api_keys
        api_keys.get_key = lambda k, s=None: MagicMock(id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET, status=StatusMixin.STATUS_ENABLED)
        app.api_keys = api_keys
        ds = MagicMock()
        ds.get_resource.side_effect = StormpathError({'developerMessage': 'No username on account.'})
        client = MagicMock(data_store=ds)
        app.accounts.get.return_value = Account(client=client, href='account')
        basic_auth = base64.b64encode('{}:{}'.format(FAKE_CLIENT_ID, FAKE_CLIENT_SECRET).encode('utf-8'))
        uri = 'https://example.com/get'
        http_method = 'GET'
        body = {'grant_type': 'client_credentials', 'scope': 'test1'}
        headers = {'Authorization': b'Basic ' + basic_auth}
        allowed_scopes = ['test1']

        authenticator = OAuthRequestAuthenticator(app)
        result = authenticator.authenticate(headers=headers, http_method=http_method, uri=uri, body=body, scopes=allowed_scopes)

        self.assertIsNotNone(result)
        self.assertIsNotNone(result.token)

        token = result.token
        body = {}
        headers = {'Authorization': b'Bearer ' + token.token.encode('utf-8')}

        disabled_api_key = MagicMock(id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET, status=StatusMixin.STATUS_DISABLED)
        disabled_api_key.is_enabled.return_value = False

        api_keys.get_key = lambda k, s=None: disabled_api_key

        result = authenticator.authenticate(headers=headers, http_method=http_method, uri=uri, body=body, scopes=allowed_scopes)

        self.assertIsNone(result)

    def test_invalid_grant_type_no_token_gets_generated(self):
        app = MagicMock()
        app._client.auth.secret = 'fakeApiKeyProperties.secret'
        app.href = 'HREF'
        api_keys = MagicMock()
        api_keys.get_key = lambda k, s=None: MagicMock(id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET, status=StatusMixin.STATUS_ENABLED)
        app.api_keys = api_keys
        basic_auth = base64.b64encode("{}:{}".format(FAKE_CLIENT_ID, FAKE_CLIENT_SECRET).encode('utf-8'))
        uri = 'https://example.com/get'
        http_method = 'GET'
        body = {'grant_type': 'invalid_grant', 'scope': 'test1'}
        headers = {'Authorization': b'Basic ' + basic_auth}
        allowed_scopes = ['test1']

        authenticator = OAuthRequestAuthenticator(app)
        result = authenticator.authenticate(headers=headers, http_method=http_method, uri=uri, body=body, scopes=allowed_scopes)

        self.assertIsNotNone(result)
        self.assertIsNone(result.token)


class OAuthBearerRequestAuthenticatorTest(TestCase):

    def test_basic_api_auth_fails(self):
        app = MagicMock()
        app._client.auth.secret = 'fakeApiKeyProperties.secret'
        app.href = 'HREF'
        api_keys = MagicMock()
        api_keys.get_key = lambda k, s=None: MagicMock(id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET, status=StatusMixin.STATUS_ENABLED)
        app.api_keys = api_keys
        basic_auth = base64.b64encode('{}:{}'.format(FAKE_CLIENT_ID, FAKE_CLIENT_SECRET).encode('utf-8'))
        uri = 'https://example.com/get'
        http_method = 'GET'
        body = {}
        headers = {'Authorization': b'Basic ' + basic_auth}
        allowed_scopes = ['test1']

        authenticator = OAuthBearerRequestAuthenticator(app)
        result = authenticator.authenticate(headers=headers, http_method=http_method, uri=uri, body=body, scopes=allowed_scopes)

        self.assertIsNone(result)

    def test_basic_api_auth_with_generating_bearer_token_fails(self):
        app = MagicMock()
        app._client.auth.secret = 'fakeApiKeyProperties.secret'
        app.href = 'HREF'
        api_keys = MagicMock()
        api_keys.get_key = lambda k, s=None: MagicMock(id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET, status=StatusMixin.STATUS_ENABLED)
        app.api_keys = api_keys
        basic_auth = base64.b64encode('{}:{}'.format(FAKE_CLIENT_ID, FAKE_CLIENT_SECRET).encode('utf-8'))
        uri = 'https://example.com/get'
        http_method = 'GET'
        body = {'grant_type': 'client_credentials', 'scope': 'test1'}
        headers = {'Authorization': b'Basic ' + basic_auth}
        allowed_scopes = ['test1']

        authenticator = OAuthBearerRequestAuthenticator(app)
        result = authenticator.authenticate(headers=headers, http_method=http_method, uri=uri, body=body, scopes=allowed_scopes)

        self.assertIsNone(result)

    def test_bearer_api_auth(self):
        app = MagicMock()
        app._client.auth.secret = 'fakeApiKeyProperties.secret'
        app.href = 'HREF'
        api_keys = MagicMock()
        api_keys.get_key = lambda k, s=None: MagicMock(id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET, status=StatusMixin.STATUS_ENABLED)
        app.api_keys = api_keys
        basic_auth = base64.b64encode('{}:{}'.format(FAKE_CLIENT_ID, FAKE_CLIENT_SECRET).encode('utf-8'))
        uri = 'https://example.com/get'
        http_method = 'GET'
        body = {'grant_type': 'client_credentials', 'scope': 'test1'}
        headers = {'Authorization': b'Basic ' + basic_auth}
        allowed_scopes = ['test1']

        authenticator = OAuthRequestAuthenticator(app)
        result = authenticator.authenticate(headers=headers, http_method=http_method, uri=uri, body=body, scopes=allowed_scopes)

        self.assertIsNotNone(result)
        self.assertIsNotNone(result.token)

        token = result.token
        body = {}
        headers = {'Authorization': b'Bearer ' + token.token.encode('utf-8')}

        authenticator = OAuthBearerRequestAuthenticator(app)
        result = authenticator.authenticate(headers=headers, http_method=http_method, uri=uri, body=body, scopes=allowed_scopes)

        self.assertIsNotNone(result)
        self.assertEquals(result.token.token, token.token)

    def test_bearer_api_auth_with_unicode(self):
        app = MagicMock()
        app._client.auth.secret = 'fakeApiKeyProperties.secret'
        app.href = 'HREF'
        api_keys = MagicMock()
        api_keys.get_key = lambda k, s=None: MagicMock(id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET, status=StatusMixin.STATUS_ENABLED)
        app.api_keys = api_keys
        basic_auth = base64.b64encode('{}:{}'.format(FAKE_CLIENT_ID, FAKE_CLIENT_SECRET).encode('utf-8'))
        uri = 'https://example.com/get'
        http_method = 'GET'
        body = {'grant_type': 'client_credentials', 'scope': 'test1'}
        headers = {'Authorization': u('Basic ') + basic_auth.decode('utf-8')}
        allowed_scopes = ['test1']

        authenticator = OAuthRequestAuthenticator(app)
        result = authenticator.authenticate(headers=headers, http_method=http_method, uri=uri, body=body, scopes=allowed_scopes)

        self.assertIsNotNone(result)
        self.assertIsNotNone(result.token)

        token = result.token
        body = {}
        headers = {'Authorization': b'Bearer ' + token.token.encode('utf-8')}

        authenticator = OAuthBearerRequestAuthenticator(app)
        result = authenticator.authenticate(headers=headers, http_method=http_method, uri=uri, body=body, scopes=allowed_scopes)

        self.assertIsNotNone(result)
        self.assertEquals(result.token.token, token.token)

    def test_bearer_api_auth_with_token_in_url(self):
        app = MagicMock()
        app._client.auth.secret = 'fakeApiKeyProperties.secret'
        app.href = 'HREF'
        api_keys = MagicMock()
        api_keys.get_key = lambda k, s=None: MagicMock(id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET, status=StatusMixin.STATUS_ENABLED)
        app.api_keys = api_keys
        basic_auth = base64.b64encode('{}:{}'.format(FAKE_CLIENT_ID, FAKE_CLIENT_SECRET).encode('utf-8'))
        body = {'grant_type': 'client_credentials', 'scope': 'test1'}
        headers = {'Authorization': b'Basic ' + basic_auth}
        allowed_scopes = ['test1']

        authenticator = OAuthRequestAuthenticator(app)
        result = authenticator.authenticate(headers=headers, body=body, scopes=allowed_scopes)

        self.assertIsNotNone(result)
        self.assertIsNotNone(result.token)

        token = result.token
        uri = 'https://example.com/get?access_token=%s' % (token.token)

        authenticator = OAuthBearerRequestAuthenticator(app)
        result = authenticator.authenticate(headers={}, uri=uri, body=body, scopes=allowed_scopes)

        self.assertIsNotNone(result)
        self.assertEquals(result.token.token, token.token)

    def test_bearer_api_auth_with_token_in_body(self):
        app = MagicMock()
        app._client.auth.secret = 'fakeApiKeyProperties.secret'
        app.href = 'HREF'
        api_keys = MagicMock()
        api_keys.get_key = lambda k, s=None: MagicMock(id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET, status=StatusMixin.STATUS_ENABLED)
        app.api_keys = api_keys
        basic_auth = base64.b64encode('{}:{}'.format(FAKE_CLIENT_ID, FAKE_CLIENT_SECRET).encode('utf-8'))
        body = {'grant_type': 'client_credentials', 'scope': 'test1'}
        headers = {'Authorization': b'Basic ' + basic_auth}
        allowed_scopes = ['test1']

        authenticator = OAuthRequestAuthenticator(app)
        result = authenticator.authenticate(headers=headers, body=body, scopes=allowed_scopes)

        self.assertIsNotNone(result)
        self.assertIsNotNone(result.token)

        token = result.token
        body = {'access_token': token.token}

        authenticator = OAuthBearerRequestAuthenticator(app)
        result = authenticator.authenticate(headers={}, body=body, scopes=allowed_scopes)

        self.assertIsNotNone(result)
        self.assertEquals(result.token.token, token.token)

    def test_bearer_api_auth_with_token_in_body_without_locations(self):
        app = MagicMock()
        app._client.auth.secret = 'fakeApiKeyProperties.secret'
        app.href = 'HREF'
        api_keys = MagicMock()
        api_keys.get_key = lambda k, s=None: MagicMock(id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET, status=StatusMixin.STATUS_ENABLED)
        app.api_keys = api_keys
        basic_auth = base64.b64encode('{}:{}'.format(FAKE_CLIENT_ID, FAKE_CLIENT_SECRET).encode('utf-8'))
        body = {'grant_type': 'client_credentials', 'scope': 'test1'}
        headers = {'Authorization': b'Basic ' + basic_auth}
        allowed_scopes = ['test1']

        authenticator = OAuthRequestAuthenticator(app)
        result = authenticator.authenticate(headers=headers, body=body, scopes=allowed_scopes)

        self.assertIsNotNone(result)
        self.assertIsNotNone(result.token)

        token = result.token
        body = {'access_token': token.token}

        authenticator = OAuthBearerRequestAuthenticator(app)
        result = authenticator.authenticate(headers={}, body=body, scopes=allowed_scopes)

        self.assertIsNotNone(result)
        self.assertEquals(result.token.token, token.token)

    def test_valid_bearer_token_but_deleted_api_key(self):
        app = MagicMock()
        app._client.auth.secret = 'fakeApiKeyProperties.secret'
        app.href = 'HREF'
        api_keys = MagicMock()
        api_keys.get_key = lambda k, s=None: MagicMock(id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET, status=StatusMixin.STATUS_ENABLED)
        app.api_keys = api_keys
        ds = MagicMock()
        ds.get_resource.side_effect = StormpathError({'developerMessage': 'No username on account.'})
        client = MagicMock(data_store=ds)
        app.accounts.get.return_value = Account(client=client, href='account')
        basic_auth = base64.b64encode('{}:{}'.format(FAKE_CLIENT_ID, FAKE_CLIENT_SECRET).encode('utf-8'))
        uri = 'https://example.com/get'
        http_method = 'GET'
        body = {'grant_type': 'client_credentials', 'scope': 'test1'}
        headers = {'Authorization': b'Basic ' + basic_auth}
        allowed_scopes = ['test1']

        authenticator = OAuthRequestAuthenticator(app)
        result = authenticator.authenticate(headers=headers, http_method=http_method, uri=uri, body=body, scopes=allowed_scopes)

        self.assertIsNotNone(result)
        self.assertIsNotNone(result.token)

        token = result.token
        body = {}
        headers = {'Authorization': b'Bearer ' + token.token.encode('utf-8')}
        api_keys.get_key = lambda k, s=None: None

        authenticator = OAuthBearerRequestAuthenticator(app)
        result = authenticator.authenticate(headers=headers, http_method=http_method, uri=uri, body=body, scopes=allowed_scopes)

        self.assertIsNone(result)

    def test_valid_bearer_token_but_disabled_api_key(self):
        app = MagicMock()
        app._client.auth.secret = 'fakeApiKeyProperties.secret'
        app.href = 'HREF'
        api_keys = MagicMock()
        api_keys.get_key = lambda k, s=None: MagicMock(id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET, status=StatusMixin.STATUS_ENABLED)
        app.api_keys = api_keys
        api_keys.get_key = lambda k, s=None: MagicMock(id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET, status=StatusMixin.STATUS_ENABLED)
        app.api_keys = api_keys
        ds = MagicMock()
        ds.get_resource.side_effect = StormpathError({'developerMessage': 'No username on account.'})
        client = MagicMock(data_store=ds)
        app.accounts.get.return_value = Account(client=client, href='account')
        basic_auth = base64.b64encode('{}:{}'.format(FAKE_CLIENT_ID, FAKE_CLIENT_SECRET).encode('utf-8'))
        uri = 'https://example.com/get'
        http_method = 'GET'
        body = {'grant_type': 'client_credentials', 'scope': 'test1'}
        headers = {'Authorization': b'Basic ' + basic_auth}
        allowed_scopes = ['test1']

        authenticator = OAuthRequestAuthenticator(app)
        result = authenticator.authenticate(headers=headers, http_method=http_method, uri=uri, body=body, scopes=allowed_scopes)

        self.assertIsNotNone(result)
        self.assertIsNotNone(result.token)

        token = result.token
        body = {}
        headers = {'Authorization': b'Bearer ' + token.token.encode('utf-8')}
        disabled_api_key = MagicMock(id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET, status=StatusMixin.STATUS_DISABLED)
        disabled_api_key.is_enabled.return_value = False
        api_keys.get_key = lambda k, s=None: disabled_api_key

        authenticator = OAuthBearerRequestAuthenticator(app)
        result = authenticator.authenticate(headers=headers, http_method=http_method, uri=uri, body=body, scopes=allowed_scopes)

        self.assertIsNone(result)


class OAuthClientCredentialsRequestAuthenticatorTest(TestCase):

    def test_basic_api_auth_fails(self):
        app = MagicMock()
        app._client.auth.secret = 'fakeApiKeyProperties.secret'
        app.href = 'HREF'
        api_keys = MagicMock()
        api_keys.get_key = lambda k, s=None: MagicMock(id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET, status=StatusMixin.STATUS_ENABLED)
        app.api_keys = api_keys
        basic_auth = base64.b64encode('{}:{}'.format(FAKE_CLIENT_ID, FAKE_CLIENT_SECRET).encode('utf-8'))
        uri = 'https://example.com/get'
        http_method = 'GET'
        body = {}
        headers = {'Authorization': b'Basic ' + basic_auth}
        allowed_scopes = ['test1']

        authenticator = OAuthClientCredentialsRequestAuthenticator(app)
        result = authenticator.authenticate(headers=headers, http_method=http_method, uri=uri, body=body, scopes=allowed_scopes)

        self.assertIsNone(result)

    def test_basic_api_auth_with_generating_bearer_token(self):
        app = MagicMock()
        app._client.auth.secret = 'fakeApiKeyProperties.secret'
        app.href = 'HREF'
        api_keys = MagicMock()
        api_keys.get_key = lambda k, s=None: MagicMock(id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET, status=StatusMixin.STATUS_ENABLED)
        app.api_keys = api_keys
        basic_auth = base64.b64encode('{}:{}'.format(FAKE_CLIENT_ID, FAKE_CLIENT_SECRET).encode('utf-8'))
        uri = 'https://example.com/get'
        http_method = 'GET'
        body = {'grant_type': 'client_credentials', 'scope': 'test1'}
        headers = {'Authorization': b'Basic ' + basic_auth}
        allowed_scopes = ['test1']

        authenticator = OAuthClientCredentialsRequestAuthenticator(app)
        result = authenticator.authenticate(headers=headers, http_method=http_method, uri=uri, body=body, scopes=allowed_scopes)

        self.assertIsNotNone(result)
        self.assertIsNotNone(result.api_key)
        self.assertIsNotNone(result.token)
        self.assertEquals(result.token.scopes, ['test1'])

    def test_basic_api_auth_with_invalid_scope_no_token_get_generated(self):
        app = MagicMock()
        app._client.auth.secret = 'fakeApiKeyProperties.secret'
        app.href = 'HREF'
        api_keys = MagicMock()
        api_keys.get_key = lambda k, s=None: MagicMock(id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET, status=StatusMixin.STATUS_ENABLED)
        app.api_keys = api_keys
        basic_auth = base64.b64encode('{}:{}'.format(FAKE_CLIENT_ID, FAKE_CLIENT_SECRET).encode('utf-8'))
        uri = 'https://example.com/get'
        http_method = 'GET'
        body = {'grant_type': 'client_credentials', 'scope': 'invalid_scope'}
        headers = {'Authorization': b'Basic ' + basic_auth}
        allowed_scopes = ['test1']

        authenticator = OAuthClientCredentialsRequestAuthenticator(app)
        result = authenticator.authenticate(headers=headers, http_method=http_method, uri=uri, body=body, scopes=allowed_scopes)

        self.assertIsNotNone(result)
        self.assertIsNone(result.token)

    def test_bearer_api_auth(self):
        app = MagicMock()
        app._client.auth.secret = 'fakeApiKeyProperties.secret'
        app.href = 'HREF'
        api_keys = MagicMock()
        api_keys.get_key = lambda k, s=None: MagicMock(id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET, status=StatusMixin.STATUS_ENABLED)
        app.api_keys = api_keys
        basic_auth = base64.b64encode('{}:{}'.format(FAKE_CLIENT_ID, FAKE_CLIENT_SECRET).encode('utf-8'))
        uri = 'https://example.com/get'
        http_method = 'GET'
        body = {'grant_type': 'client_credentials', 'scope': 'test1'}
        headers = {'Authorization': b'Basic ' + basic_auth}
        allowed_scopes = ['test1']

        authenticator = OAuthClientCredentialsRequestAuthenticator(app)
        result = authenticator.authenticate(headers=headers, http_method=http_method, uri=uri, body=body, scopes=allowed_scopes)

        self.assertIsNotNone(result)
        self.assertIsNotNone(result.token)

        token = result.token
        body = {}
        headers = {'Authorization': b'Bearer ' + token.token.encode('utf-8')}

        result = authenticator.authenticate(headers=headers, http_method=http_method, uri=uri, body=body, scopes=allowed_scopes)

        self.assertIsNone(result)

    def test_bearer_api_auth_with_unicode(self):
        app = MagicMock()
        app._client.auth.secret = 'fakeApiKeyProperties.secret'
        app.href = 'HREF'
        api_keys = MagicMock()
        api_keys.get_key = lambda k, s=None: MagicMock(id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET, status=StatusMixin.STATUS_ENABLED)
        app.api_keys = api_keys
        basic_auth = base64.b64encode('{}:{}'.format(FAKE_CLIENT_ID, FAKE_CLIENT_SECRET).encode('utf-8'))
        uri = 'https://example.com/get'
        http_method = 'GET'
        body = {'grant_type': 'client_credentials', 'scope': 'test1'}
        headers = {'Authorization': u('Basic ') + basic_auth.decode('utf-8')}
        allowed_scopes = ['test1']

        authenticator = OAuthClientCredentialsRequestAuthenticator(app)
        result = authenticator.authenticate(headers=headers, http_method=http_method, uri=uri, body=body, scopes=allowed_scopes)

        self.assertIsNotNone(result)
        self.assertIsNotNone(result.token)

        token = result.token
        body = {}
        headers = {'Authorization': b'Bearer ' + token.token.encode('utf-8')}

        result = authenticator.authenticate(headers=headers, http_method=http_method, uri=uri, body=body, scopes=allowed_scopes)

        self.assertIsNone(result)

    def test_bearer_api_auth_with_token_in_url(self):
        app = MagicMock()
        app._client.auth.secret = 'fakeApiKeyProperties.secret'
        app.href = 'HREF'
        api_keys = MagicMock()
        api_keys.get_key = lambda k, s=None: MagicMock(id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET, status=StatusMixin.STATUS_ENABLED)
        app.api_keys = api_keys
        basic_auth = base64.b64encode('{}:{}'.format(FAKE_CLIENT_ID, FAKE_CLIENT_SECRET).encode('utf-8'))
        body = {'grant_type': 'client_credentials', 'scope': 'test1'}
        headers = {'Authorization': b'Basic ' + basic_auth}
        allowed_scopes = ['test1']

        authenticator = OAuthClientCredentialsRequestAuthenticator(app)
        result = authenticator.authenticate(headers=headers, body=body, scopes=allowed_scopes)

        self.assertIsNotNone(result)
        self.assertIsNotNone(result.token)

        token = result.token
        uri = 'https://example.com/get?access_token=%s' % (token.token)

        result = authenticator.authenticate(headers={}, uri=uri, body=body, scopes=allowed_scopes)
        self.assertIsNone(result)

    def test_bearer_api_auth_with_token_in_body(self):
        app = MagicMock()
        app._client.auth.secret = 'fakeApiKeyProperties.secret'
        app.href = 'HREF'
        api_keys = MagicMock()
        api_keys.get_key = lambda k, s=None: MagicMock(id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET, status=StatusMixin.STATUS_ENABLED)
        app.api_keys = api_keys
        basic_auth = base64.b64encode('{}:{}'.format(FAKE_CLIENT_ID, FAKE_CLIENT_SECRET).encode('utf-8'))
        body = {'grant_type': 'client_credentials', 'scope': 'test1'}
        headers = {'Authorization': b'Basic ' + basic_auth}
        allowed_scopes = ['test1']

        authenticator = OAuthClientCredentialsRequestAuthenticator(app)
        result = authenticator.authenticate(headers=headers, body=body, scopes=allowed_scopes)

        self.assertIsNotNone(result)
        self.assertIsNotNone(result.token)

        token = result.token
        body = {'access_token': token.token}

        authenticator = OAuthRequestAuthenticator(app)
        result = authenticator.authenticate(headers={}, body=body, scopes=allowed_scopes)

        self.assertIsNotNone(result)
        self.assertEquals(result.token.token, token.token)

    def test_bearer_api_auth_with_token_in_body_without_locations(self):
        app = MagicMock()
        app._client.auth.secret = 'fakeApiKeyProperties.secret'
        app.href = 'HREF'
        api_keys = MagicMock()
        api_keys.get_key = lambda k, s=None: MagicMock(id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET, status=StatusMixin.STATUS_ENABLED)
        app.api_keys = api_keys
        basic_auth = base64.b64encode('{}:{}'.format(FAKE_CLIENT_ID, FAKE_CLIENT_SECRET).encode('utf-8'))
        body = {'grant_type': 'client_credentials', 'scope': 'test1'}
        headers = {'Authorization': b'Basic ' + basic_auth}
        allowed_scopes = ['test1']

        authenticator = OAuthClientCredentialsRequestAuthenticator(app)
        result = authenticator.authenticate(headers=headers, body=body, scopes=allowed_scopes)

        self.assertIsNotNone(result)
        self.assertIsNotNone(result.token)

        token = result.token
        body = {'access_token': token.token}

        authenticator = OAuthRequestAuthenticator(app)
        result = authenticator.authenticate(headers={}, body=body, scopes=allowed_scopes)

        self.assertIsNotNone(result)
        self.assertEquals(result.token.token, token.token)

    def test_valid_bearer_token_but_deleted_api_key(self):
        app = MagicMock()
        app._client.auth.secret = 'fakeApiKeyProperties.secret'
        app.href = 'HREF'
        api_keys = MagicMock()
        api_keys.get_key = lambda k, s=None: MagicMock(id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET, status=StatusMixin.STATUS_ENABLED)
        app.api_keys = api_keys
        ds = MagicMock()
        ds.get_resource.side_effect = StormpathError({'developerMessage': 'No username on account.'})
        client = MagicMock(data_store=ds)
        app.accounts.get.return_value = Account(client=client, href='account')
        basic_auth = base64.b64encode('{}:{}'.format(FAKE_CLIENT_ID, FAKE_CLIENT_SECRET).encode('utf-8'))
        uri = 'https://example.com/get'
        http_method = 'GET'
        body = {'grant_type': 'client_credentials', 'scope': 'test1'}
        headers = {'Authorization': b'Basic ' + basic_auth}
        allowed_scopes = ['test1']

        authenticator = OAuthClientCredentialsRequestAuthenticator(app)
        result = authenticator.authenticate(headers=headers, http_method=http_method, uri=uri, body=body, scopes=allowed_scopes)

        self.assertIsNotNone(result)
        self.assertIsNotNone(result.token)

        token = result.token
        body = {}
        headers = {'Authorization': b'Bearer ' + token.token.encode('utf-8')}
        api_keys.get_key = lambda k, s=None: None

        authenticator = OAuthRequestAuthenticator(app)
        result = authenticator.authenticate(headers=headers, http_method=http_method, uri=uri, body=body, scopes=allowed_scopes)

        self.assertIsNone(result)

    def test_valid_bearer_token_but_disabled_api_key(self):
        app = MagicMock()
        app._client.auth.secret = 'fakeApiKeyProperties.secret'
        app.href = 'HREF'
        api_keys = MagicMock()
        api_keys.get_key = lambda k, s=None: MagicMock(id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET, status=StatusMixin.STATUS_ENABLED)
        app.api_keys = api_keys
        api_keys.get_key = lambda k, s=None: MagicMock(id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET, status=StatusMixin.STATUS_ENABLED)
        app.api_keys = api_keys
        ds = MagicMock()
        ds.get_resource.side_effect = StormpathError({'developerMessage': 'No username on account.'})
        client = MagicMock(data_store=ds)
        app.accounts.get.return_value = Account(client=client, href='account')
        basic_auth = base64.b64encode("{}:{}".format(FAKE_CLIENT_ID, FAKE_CLIENT_SECRET).encode('utf-8'))
        uri = 'https://example.com/get'
        http_method = 'GET'
        body = {'grant_type': 'client_credentials', 'scope': 'test1'}
        headers = {'Authorization': b'Basic ' + basic_auth}
        allowed_scopes = ['test1']

        authenticator = OAuthClientCredentialsRequestAuthenticator(app)
        result = authenticator.authenticate(headers=headers, http_method=http_method, uri=uri, body=body, scopes=allowed_scopes)

        self.assertIsNotNone(result)
        self.assertIsNotNone(result.token)

        token = result.token
        body = {}
        headers = {'Authorization': b'Bearer ' + token.token.encode('utf-8')}
        disabled_api_key = MagicMock(id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET, status=StatusMixin.STATUS_DISABLED)
        disabled_api_key.is_enabled.return_value = False
        api_keys.get_key = lambda k, s=None: disabled_api_key

        authenticator = OAuthRequestAuthenticator(app)
        result = authenticator.authenticate(headers=headers, http_method=http_method, uri=uri, body=body, scopes=allowed_scopes)

        self.assertIsNone(result)

    def test_invalid_grant_type_no_token_gets_generated(self):
        app = MagicMock()
        app._client.auth.secret = 'fakeApiKeyProperties.secret'
        app.href = 'HREF'
        api_keys = MagicMock()
        api_keys.get_key = lambda k, s=None: MagicMock(id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET, status=StatusMixin.STATUS_ENABLED)
        app.api_keys = api_keys
        basic_auth = base64.b64encode('{}:{}'.format(FAKE_CLIENT_ID, FAKE_CLIENT_SECRET).encode('utf-8'))
        uri = 'https://example.com/get'
        http_method = 'GET'
        body = {'grant_type': 'invalid_grant', 'scope': 'test1'}
        headers = {'Authorization': b'Basic ' + basic_auth}
        allowed_scopes = ['test1']

        authenticator = OAuthClientCredentialsRequestAuthenticator(app)
        result = authenticator.authenticate(headers=headers, http_method=http_method, uri=uri, body=body, scopes=allowed_scopes)

        self.assertIsNotNone(result)
        self.assertIsNone(result.token)


class AuthenticatorsTest(TestCase):

    @patch('stormpath.http.Session')
    def setUp(self, session):
        self.session = session
        tenant_return = MagicMock(
            status_code = 200,
            json = MagicMock(return_value={'applications': {'href': 'applications'}}),
        )
        client = Client(api_key={'id': 'MyId', 'secret': 'Shush!'}, method='basic')

        self.session.return_value.request.return_value = tenant_return
        self.application = client.applications.get('application_url')

    def test_password_grant_authenticator(self):
        pga_return = MagicMock(
            status_code = 200,
            json = MagicMock(return_value={
                'stormpath_access_token_href': 'href',
                'access_token': 'token',
                'expires_in': 3600,
                'token_type': 'bearer',
                'refresh_token': 'token',
            })
        )

        pga = PasswordGrantAuthenticator(self.application)
        self.session.return_value.request.return_value = pga_return
        pga.authenticate('some@user.com', 'secret')

        self.session.return_value.request.assert_called_with('POST', 'https://api.stormpath.com/v1/applications/application_url/oauth/token',
            headers = {'Content-Type': 'application/x-www-form-urlencoded'},
            allow_redirects = False,
            params = OrderedDict([
                ('grant_type', 'password'),
                ('password', 'secret'),
                ('username', 'some@user.com')
            ]),
            data = None
        )

    def test_refresh_grant_authenticator(self):
        rga_return = MagicMock(
            status_code = 200,
            json = MagicMock(return_value={
                'stormpath_access_token_href': 'href',
                'access_token': 'token',
                'expires_in': 3600,
                'token_type': 'bearer',
                'refresh_token': 'token',
            })
        )

        rga = RefreshGrantAuthenticator(self.application)
        self.session.return_value.request.return_value = rga_return
        rga.authenticate('refresh-token')

        self.session.return_value.request.assert_called_with('POST', 'https://api.stormpath.com/v1/applications/application_url/oauth/token',
            headers = {'Content-Type': 'application/x-www-form-urlencoded'},
            allow_redirects = False,
            params = OrderedDict([
                ('grant_type', 'refresh_token'),
                ('refresh_token', 'refresh-token')
            ]),
            data = None
        )

    def test_id_site_token_authenticator(self):
        ist_return = MagicMock(
            status_code = 200,
            json = MagicMock(return_value={
                'stormpath_access_token_href': 'href',
                'access_token': 'token',
                'expires_in': 3600,
                'token_type': 'bearer',
                'refresh_token': 'token',
            })
        )

        ista = IdSiteTokenAuthenticator(self.application)
        self.session.return_value.request.return_value = ist_return
        ista.authenticate('id-site-token')

        self.session.return_value.request.assert_called_with('POST', 'https://api.stormpath.com/v1/applications/application_url/oauth/token',
            headers = {'Content-Type': 'application/x-www-form-urlencoded'},
            allow_redirects = False,
            params = OrderedDict([
                ('grant_type', 'id_site_token'),
                ('token', 'id-site-token')
            ]),
            data = None
        )

"""Live tests of client authentication against the Stormpath service API."""
import base64
from six import u
from time import sleep

from .base import ApiKeyBase
from stormpath.api_auth import *
from stormpath.error import Error as StormpathError
from stormpath.resources import AuthToken, Expansion


class TestApiRequestAuthenticator(ApiKeyBase):

    def test_basic_api_authentication_succeeds(self):
        _, acc = self.create_account(self.app.accounts)
        api_key = self.create_api_key(acc)

        headers = {
            'Authorization':
                b'Basic ' + base64.b64encode(
                    "{}:{}".format(api_key.id, api_key.secret).encode('utf-8'))
        }

        authenticator = ApiRequestAuthenticator(self.app)
        result = authenticator.authenticate(headers=headers)

        self.assertIsNotNone(result)
        self.assertEqual(api_key.id, result.api_key.id)
        self.assertEqual(api_key.secret, result.api_key.secret)
        self.assertEqual(acc.href, result.api_key.account.href)

    def test_basic_api_authentication_with_unicode_succeeds(self):
        _, acc = self.create_account(self.app.accounts)
        api_key = self.create_api_key(acc)

        b64_key = base64.b64encode(
            '{}:{}'.format(api_key.id, api_key.secret).encode('utf-8'))
        headers = {
            'Authorization':
                u('Basic ') + b64_key.decode('utf-8')
        }

        authenticator = ApiRequestAuthenticator(self.app)
        result = authenticator.authenticate(headers=headers)

        self.assertIsNotNone(result)
        self.assertEqual(api_key.id, result.api_key.id)
        self.assertEqual(api_key.secret, result.api_key.secret)
        self.assertEqual(acc.href, result.api_key.account.href)

    def test_basic_api_authentication_fails(self):
        _, acc = self.create_account(self.app.accounts)
        api_key = self.create_api_key(acc)

        headers = {
            'Authorization':
                b'Basic ' + base64.b64encode(
                    "{}:{}".format(api_key.id, 'INVALID').encode('utf-8'))
        }

        authenticator = ApiRequestAuthenticator(self.app)
        result = authenticator.authenticate(headers=headers)

        self.assertIsNone(result)

    def test_bearer_api_authentication_succeeds(self):
        _, acc = self.create_account(self.app.accounts)
        api_key = self.create_api_key(acc)

        headers = {
            'Authorization':
                b'Basic ' + base64.b64encode(
                    "{}:{}".format(api_key.id, api_key.secret).encode('utf-8'))
        }
        body = {'grant_type': 'client_credentials', 'scope': 's1 s2'}
        scopes = ['s1', 's2']

        authenticator = ApiRequestAuthenticator(self.app)
        result = authenticator.authenticate(
            body=body, headers=headers, scopes=scopes)

        self.assertEqual(api_key.id, result.api_key.id)
        self.assertEqual(api_key.secret, result.api_key.secret)
        self.assertEqual(acc.href, result.api_key.account.href)
        self.assertEqual(result.token.scopes, scopes)

        headers = {
            'Authorization': b'Bearer ' + result.token.token.encode('utf-8')}

        authenticator = ApiRequestAuthenticator(self.app)
        result = authenticator.authenticate(headers=headers, scopes=scopes)

        self.assertIsNotNone(result)
        self.assertEqual(acc.href, result.account.href)

    def test_bearer_api_authentication_without_scopes_and_body_succeeds(self):
        _, acc = self.create_account(self.app.accounts)
        api_key = self.create_api_key(acc)

        headers = {
            'Authorization':
                b'Basic ' + base64.b64encode(
                    "{}:{}".format(api_key.id, api_key.secret).encode('utf-8'))
        }
        uri = 'https://example.com/get?grant_type=client_credentials'

        authenticator = ApiRequestAuthenticator(self.app)
        result = authenticator.authenticate(uri=uri, headers=headers)

        self.assertEqual(api_key.id, result.api_key.id)
        self.assertEqual(api_key.secret, result.api_key.secret)
        self.assertEqual(acc.href, result.api_key.account.href)

        headers = {
            'Authorization': b'Bearer ' + result.token.token.encode('utf-8')}

        authenticator = ApiRequestAuthenticator(self.app)
        result = authenticator.authenticate(headers=headers)

        self.assertIsNotNone(result)
        self.assertEqual(acc.href, result.account.href)

    def test_basic_api_authentication_with_grant_type_in_uri_gets_token(self):
        _, acc = self.create_account(self.app.accounts)
        api_key = self.create_api_key(acc)

        headers = {
            'Authorization':
                b'Basic ' + base64.b64encode(
                    "{}:{}".format(api_key.id, api_key.secret).encode('utf-8'))
        }
        body = {'scope': 's1 s2'}
        scopes = ['s1', 's2']
        uri = 'https://example.com/get?grant_type=client_credentials'

        authenticator = ApiRequestAuthenticator(self.app)
        result = authenticator.authenticate(
            uri=uri, body=body, headers=headers, scopes=scopes)

        self.assertIsNotNone(result.token)
        self.assertEqual(result.token.scopes, scopes)

    def test_basic_api_auth_w_wrong_grant_type_in_uri_does_not_get_token(self):
        _, acc = self.create_account(self.app.accounts)
        api_key = self.create_api_key(acc)

        headers = {
            'Authorization':
                b'Basic ' + base64.b64encode(
                    "{}:{}".format(api_key.id, api_key.secret).encode('utf-8'))
        }
        body = {'scope': 's1 s2'}
        scopes = ['s1', 's2']
        uri = 'https://example.com/get?grant_type=invalid_grant_type'

        authenticator = ApiRequestAuthenticator(self.app)
        result = authenticator.authenticate(
            uri=uri, body=body, headers=headers, scopes=scopes)

        self.assertIsNone(result.token)

    def test_bearer_api_authentication_with_unicode_succeeds(self):
        _, acc = self.create_account(self.app.accounts)
        api_key = self.create_api_key(acc)

        b64_key = base64.b64encode(
            '{}:{}'.format(api_key.id, api_key.secret).encode('utf-8'))
        headers = {
            'Authorization': u('Basic ') + b64_key.decode('utf-8')
        }
        body = {'grant_type': 'client_credentials', 'scope': 's1 s2'}
        scopes = ['s1', 's2']

        authenticator = ApiRequestAuthenticator(self.app)
        result = authenticator.authenticate(
            body=body, headers=headers, scopes=scopes)

        self.assertEqual(api_key.id, result.api_key.id)
        self.assertEqual(api_key.secret, result.api_key.secret)
        self.assertEqual(acc.href, result.api_key.account.href)
        self.assertEqual(result.token.scopes, scopes)

        headers = {
            'Authorization': u('Bearer ') + result.token.token}

        authenticator = ApiRequestAuthenticator(self.app)
        result = authenticator.authenticate(headers=headers, scopes=scopes)

        self.assertIsNotNone(result)
        self.assertEqual(acc.href, result.account.href)

    def test_bearer_api_authentication_with_wrong_token_fails(self):
        headers = {'Authorization': b'Bearer INVALID_TOKEN'}

        authenticator = ApiRequestAuthenticator(self.app)
        result = authenticator.authenticate(headers=headers)

        self.assertIsNone(result)

    def test_bearer_api_authentication_with_wrong_scope_fails(self):
        _, acc = self.create_account(self.app.accounts)
        api_key = self.create_api_key(acc)

        headers = {
            'Authorization':
                b'Basic ' + base64.b64encode(
                    "{}:{}".format(api_key.id, api_key.secret).encode('utf-8'))
        }
        body = {'grant_type': 'client_credentials', 'scope': 's1'}

        authenticator = ApiRequestAuthenticator(self.app)
        result = authenticator.authenticate(
            body=body, headers=headers, scopes=['s1'])

        self.assertEqual(api_key.id, result.api_key.id)
        self.assertEqual(api_key.secret, result.api_key.secret)
        self.assertEqual(acc.href, result.api_key.account.href)
        self.assertEqual(result.token.scopes, ['s1'])

        headers = {
            'Authorization': b'Bearer ' + result.token.token.encode('utf-8')}

        result = authenticator.authenticate(
            headers=headers, scopes=['s1', 's2'])

        self.assertIsNone(result)

    def test_valid_bearer_token_but_deleted_api_key(self):
        _, acc = self.create_account(self.app.accounts)
        api_key = self.create_api_key(acc)

        basic_auth = base64.b64encode(
            "{}:{}".format(api_key.id, api_key.secret).encode('utf-8'))

        body = {'grant_type': 'client_credentials', 'scope': 'test1'}
        headers = {
                'Authorization': b'Basic ' + basic_auth
                }

        allowed_scopes = ['test1']

        authenticator = ApiRequestAuthenticator(self.app)
        result = authenticator.authenticate(
            body=body, headers=headers, scopes=allowed_scopes)

        self.assertIsNotNone(result)
        self.assertIsNotNone(result.token)
        token = result.token
        body = {}
        headers = {
                'Authorization': b'Bearer ' + token.token.encode('utf-8')
                }

        api_key.delete()

        result = authenticator.authenticate(
            headers=headers, scopes=allowed_scopes)

        self.assertIsNone(result)

    def test_valid_bearer_token_but_disabled_api_key(self):
        _, acc = self.create_account(self.app.accounts)
        api_key = self.create_api_key(acc)

        basic_auth = base64.b64encode(
            "{}:{}".format(api_key.id, api_key.secret).encode('utf-8'))

        body = {'grant_type': 'client_credentials', 'scope': 'test1'}
        headers = {
                'Authorization': b'Basic ' + basic_auth
                }

        allowed_scopes = ['test1']

        authenticator = ApiRequestAuthenticator(self.app)
        result = authenticator.authenticate(
            body=body, headers=headers, scopes=allowed_scopes)

        self.assertIsNotNone(result)
        self.assertIsNotNone(result.token)
        token = result.token
        body = {}
        headers = {
                'Authorization': b'Bearer ' + token.token.encode('utf-8')
                }

        api_key.status = 'disabled'
        api_key.save()

        result = authenticator.authenticate(
            headers=headers, scopes=allowed_scopes)

        self.assertIsNone(result)

    def test_invalid_grant_type_no_token_gets_generated(self):
        _, acc = self.create_account(self.app.accounts)
        api_key = self.create_api_key(acc)

        basic_auth = base64.b64encode(
            "{}:{}".format(api_key.id, api_key.secret).encode('utf-8'))

        body = {'grant_type': 'invalid_grant', 'scope': 'test1'}
        headers = {
                'Authorization': b'Basic ' + basic_auth
                }

        allowed_scopes = ['test1']

        authenticator = ApiRequestAuthenticator(self.app)
        result = authenticator.authenticate(
            body=body, headers=headers, scopes=allowed_scopes)

        self.assertIsNotNone(result)
        self.assertIsNone(result.token)

    def test_account_authentication_successfull(self):
        _, acc = self.create_account(self.app.accounts)
        pwd = 'Pwd123456789'
        acc.password = pwd
        acc.save()

        auth_result = self.app.authenticate_account(acc.username, pwd)
        at = auth_result.get_access_token()

        headers = {
            'Authorization': b'Bearer ' + at.token.encode('utf-8')}

        authenticator = ApiRequestAuthenticator(self.app)
        result = authenticator.authenticate(headers)
        self.assertIsNotNone(result)

    def test_account_authentication_invalid_credentials(self):
        _, acc = self.create_account(self.app.accounts)
        pwd = 'Pwd123456789'
        acc.password = pwd
        acc.save()

        with self.assertRaises(StormpathError):
            self.app.authenticate_account(acc.username, 'invalid')

    def test_account_authentication_invalid_access_token(self):
        _, acc = self.create_account(self.app.accounts)
        pwd = 'Pwd123456789'
        acc.password = pwd
        acc.save()

        auth_result = self.app.authenticate_account(acc.username, pwd)
        at = auth_result.get_access_token()
        at.token = 'invalid'

        headers = {
            'Authorization': b'Bearer ' + at.token.encode('utf-8')}

        authenticator = ApiRequestAuthenticator(self.app)
        result = authenticator.authenticate(headers)
        self.assertIsNone(result)

    def test_account_authentication_with_access_token_in_url(self):
        _, acc = self.create_account(self.app.accounts)
        pwd = 'Pwd123456789'
        acc.password = pwd
        acc.save()

        auth_result = self.app.authenticate_account(acc.username, pwd)
        at = auth_result.get_access_token()

        uri = 'https://example.com/get?access_token=' + at.token

        authenticator = ApiRequestAuthenticator(self.app)
        result = authenticator.authenticate(headers={}, uri=uri)
        self.assertIsNotNone(result)

    def test_account_authentication_with_access_token_in_body(self):
        _, acc = self.create_account(self.app.accounts)
        pwd = 'Pwd123456789'
        acc.password = pwd
        acc.save()

        auth_result = self.app.authenticate_account(acc.username, pwd)
        at = auth_result.get_access_token()

        body = {'access_token': at.token}

        authenticator = ApiRequestAuthenticator(self.app)
        result = authenticator.authenticate(headers={}, body=body)
        self.assertIsNotNone(result)


class TestBasicRequestAuthenticator(ApiKeyBase):

    def test_basic_api_authentication_succeeds(self):
        _, acc = self.create_account(self.app.accounts)
        api_key = self.create_api_key(acc)

        headers = {
            'Authorization':
                b'Basic ' + base64.b64encode(
                    "{}:{}".format(api_key.id, api_key.secret).encode('utf-8'))
        }

        authenticator = BasicRequestAuthenticator(self.app)
        result = authenticator.authenticate(headers=headers)

        self.assertIsNotNone(result)
        self.assertEqual(api_key.id, result.api_key.id)
        self.assertEqual(api_key.secret, result.api_key.secret)
        self.assertEqual(acc.href, result.api_key.account.href)

    def test_basic_api_authentication_with_unicode_succeeds(self):
        _, acc = self.create_account(self.app.accounts)
        api_key = self.create_api_key(acc)

        b64_key = base64.b64encode(
            '{}:{}'.format(api_key.id, api_key.secret).encode('utf-8'))
        headers = {
            'Authorization':
                u('Basic ') + b64_key.decode('utf-8')
        }

        authenticator = BasicRequestAuthenticator(self.app)
        result = authenticator.authenticate(headers=headers)

        self.assertIsNotNone(result)
        self.assertEqual(api_key.id, result.api_key.id)
        self.assertEqual(api_key.secret, result.api_key.secret)
        self.assertEqual(acc.href, result.api_key.account.href)

    def test_basic_api_authentication_fails(self):
        _, acc = self.create_account(self.app.accounts)
        api_key = self.create_api_key(acc)

        headers = {
            'Authorization':
                b'Basic ' + base64.b64encode(
                    "{}:{}".format(api_key.id, 'INVALID').encode('utf-8'))
        }

        authenticator = BasicRequestAuthenticator(self.app)
        result = authenticator.authenticate(headers=headers)

        self.assertIsNone(result)


class TestOAuthRequestAuthenticator(ApiKeyBase):

    def test_correct_basic_api_authentication_fails(self):
        _, acc = self.create_account(self.app.accounts)
        api_key = self.create_api_key(acc)

        headers = {
            'Authorization':
                b'Basic ' + base64.b64encode(
                    "{}:{}".format(api_key.id, api_key.secret).encode('utf-8'))
        }

        authenticator = OAuthRequestAuthenticator(self.app)
        result = authenticator.authenticate(headers=headers)

        self.assertIsNone(result)

    def test_bearer_api_authentication_succeeds(self):
        _, acc = self.create_account(self.app.accounts)
        api_key = self.create_api_key(acc)

        headers = {
            'Authorization':
                b'Basic ' + base64.b64encode(
                    "{}:{}".format(api_key.id, api_key.secret).encode('utf-8'))
        }
        body = {'grant_type': 'client_credentials', 'scope': 's1 s2'}
        scopes = ['s1', 's2']

        authenticator = OAuthRequestAuthenticator(self.app)
        result = authenticator.authenticate(
            body=body, headers=headers, scopes=scopes)

        self.assertEqual(api_key.id, result.api_key.id)
        self.assertEqual(api_key.secret, result.api_key.secret)
        self.assertEqual(acc.href, result.api_key.account.href)
        self.assertEqual(result.token.scopes, scopes)

        headers = {
            'Authorization': b'Bearer ' + result.token.token.encode('utf-8')}

        result = authenticator.authenticate(headers=headers, scopes=scopes)

        self.assertIsNotNone(result)
        self.assertEqual(acc.href, result.account.href)

    def test_bearer_api_authentication_without_scopes_and_body_succeeds(self):
        _, acc = self.create_account(self.app.accounts)
        api_key = self.create_api_key(acc)

        headers = {
            'Authorization':
                b'Basic ' + base64.b64encode(
                    "{}:{}".format(api_key.id, api_key.secret).encode('utf-8'))
        }
        uri = 'https://example.com/get?grant_type=client_credentials'

        authenticator = OAuthRequestAuthenticator(self.app)
        result = authenticator.authenticate(uri=uri, headers=headers)

        self.assertEqual(api_key.id, result.api_key.id)
        self.assertEqual(api_key.secret, result.api_key.secret)
        self.assertEqual(acc.href, result.api_key.account.href)

        headers = {
            'Authorization': b'Bearer ' + result.token.token.encode('utf-8')}

        result = authenticator.authenticate(headers=headers)

        self.assertIsNotNone(result)
        self.assertEqual(acc.href, result.account.href)

    def test_basic_api_authentication_with_grant_type_in_uri_gets_token(self):
        _, acc = self.create_account(self.app.accounts)
        api_key = self.create_api_key(acc)

        headers = {
            'Authorization':
                b'Basic ' + base64.b64encode(
                    "{}:{}".format(api_key.id, api_key.secret).encode('utf-8'))
        }
        body = {'scope': 's1 s2'}
        scopes = ['s1', 's2']
        uri = 'https://example.com/get?grant_type=client_credentials'

        authenticator = OAuthRequestAuthenticator(self.app)
        result = authenticator.authenticate(
            uri=uri, body=body, headers=headers, scopes=scopes)

        self.assertIsNotNone(result.token)
        self.assertEqual(result.token.scopes, scopes)

    def test_basic_api_auth_w_wrong_grant_type_in_uri_does_not_get_token(self):
        _, acc = self.create_account(self.app.accounts)
        api_key = self.create_api_key(acc)

        headers = {
            'Authorization':
                b'Basic ' + base64.b64encode(
                    "{}:{}".format(api_key.id, api_key.secret).encode('utf-8'))
        }
        body = {'scope': 's1 s2'}
        scopes = ['s1', 's2']
        uri = 'https://example.com/get?grant_type=invalid_grant_type'

        authenticator = OAuthRequestAuthenticator(self.app)
        result = authenticator.authenticate(
            uri=uri, body=body, headers=headers, scopes=scopes)

        self.assertIsNone(result.token)

    def test_bearer_api_authentication_with_unicode_succeeds(self):
        _, acc = self.create_account(self.app.accounts)
        api_key = self.create_api_key(acc)

        b64_key = base64.b64encode(
            '{}:{}'.format(api_key.id, api_key.secret).encode('utf-8'))
        headers = {
            'Authorization': u('Basic ') + b64_key.decode('utf-8')
        }
        body = {'grant_type': 'client_credentials', 'scope': 's1 s2'}
        scopes = ['s1', 's2']

        authenticator = OAuthRequestAuthenticator(self.app)
        result = authenticator.authenticate(
            body=body, headers=headers, scopes=scopes)

        self.assertEqual(api_key.id, result.api_key.id)
        self.assertEqual(api_key.secret, result.api_key.secret)
        self.assertEqual(acc.href, result.api_key.account.href)
        self.assertEqual(result.token.scopes, scopes)

        headers = {
            'Authorization': u('Bearer ') + result.token.token}

        result = authenticator.authenticate(headers=headers, scopes=scopes)

        self.assertIsNotNone(result)
        self.assertEqual(acc.href, result.account.href)

    def test_bearer_api_authentication_with_wrong_token_fails(self):
        headers = {'Authorization': b'Bearer INVALID_TOKEN'}

        authenticator = OAuthRequestAuthenticator(self.app)
        result = authenticator.authenticate(headers=headers)

        self.assertIsNone(result)

    def test_bearer_api_authentication_with_wrong_scope_fails(self):
        _, acc = self.create_account(self.app.accounts)
        api_key = self.create_api_key(acc)

        headers = {
            'Authorization':
                b'Basic ' + base64.b64encode(
                    "{}:{}".format(api_key.id, api_key.secret).encode('utf-8'))
        }
        body = {'grant_type': 'client_credentials', 'scope': 's1'}

        authenticator = OAuthRequestAuthenticator(self.app)
        result = authenticator.authenticate(
            body=body, headers=headers, scopes=['s1'])

        self.assertEqual(api_key.id, result.api_key.id)
        self.assertEqual(api_key.secret, result.api_key.secret)
        self.assertEqual(acc.href, result.api_key.account.href)
        self.assertEqual(result.token.scopes, ['s1'])

        headers = {
            'Authorization': b'Bearer ' + result.token.token.encode('utf-8')}

        result = authenticator.authenticate(
            headers=headers, scopes=['s1', 's2'])

        self.assertIsNone(result)

    def test_valid_bearer_token_but_deleted_api_key(self):
        _, acc = self.create_account(self.app.accounts)
        api_key = self.create_api_key(acc)

        basic_auth = base64.b64encode(
            "{}:{}".format(api_key.id, api_key.secret).encode('utf-8'))

        body = {'grant_type': 'client_credentials', 'scope': 'test1'}
        headers = {
                'Authorization': b'Basic ' + basic_auth
                }

        allowed_scopes = ['test1']

        authenticator = OAuthRequestAuthenticator(self.app)
        result = authenticator.authenticate(
            body=body, headers=headers, scopes=allowed_scopes)

        self.assertIsNotNone(result)
        self.assertIsNotNone(result.token)
        token = result.token
        body = {}
        headers = {
                'Authorization': b'Bearer ' + token.token.encode('utf-8')
                }

        api_key.delete()

        result = authenticator.authenticate(
            headers=headers, scopes=allowed_scopes)

        self.assertIsNone(result)

    def test_valid_bearer_token_but_disabled_api_key(self):
        _, acc = self.create_account(self.app.accounts)
        api_key = self.create_api_key(acc)

        basic_auth = base64.b64encode(
            "{}:{}".format(api_key.id, api_key.secret).encode('utf-8'))

        body = {'grant_type': 'client_credentials', 'scope': 'test1'}
        headers = {
                'Authorization': b'Basic ' + basic_auth
                }

        allowed_scopes = ['test1']

        authenticator = OAuthRequestAuthenticator(self.app)
        result = authenticator.authenticate(
            body=body, headers=headers, scopes=allowed_scopes)

        self.assertIsNotNone(result)
        self.assertIsNotNone(result.token)
        token = result.token
        body = {}
        headers = {
                'Authorization': b'Bearer ' + token.token.encode('utf-8')
                }

        api_key.status = 'disabled'
        api_key.save()

        result = authenticator.authenticate(
            headers=headers, scopes=allowed_scopes)

        self.assertIsNone(result)

    def test_invalid_grant_type_no_token_gets_generated(self):
        _, acc = self.create_account(self.app.accounts)
        api_key = self.create_api_key(acc)

        basic_auth = base64.b64encode(
            "{}:{}".format(api_key.id, api_key.secret).encode('utf-8'))

        body = {'grant_type': 'invalid_grant', 'scope': 'test1'}
        headers = {
                'Authorization': b'Basic ' + basic_auth
                }

        allowed_scopes = ['test1']

        authenticator = OAuthRequestAuthenticator(self.app)
        result = authenticator.authenticate(
            body=body, headers=headers, scopes=allowed_scopes)

        self.assertIsNotNone(result)
        self.assertIsNone(result.token)

    def test_account_authentication_successfull(self):
        _, acc = self.create_account(self.app.accounts)
        pwd = 'Pwd123456789'
        acc.password = pwd
        acc.save()

        auth_result = self.app.authenticate_account(acc.username, pwd)
        at = auth_result.get_access_token()

        headers = {
            'Authorization': b'Bearer ' + at.token.encode('utf-8')}

        authenticator = OAuthRequestAuthenticator(self.app)
        result = authenticator.authenticate(headers)
        self.assertIsNotNone(result)


class TestOAuthBearerRequestAuthenticator(ApiKeyBase):

    def test_correct_basic_api_authentication_fails(self):
        _, acc = self.create_account(self.app.accounts)
        api_key = self.create_api_key(acc)

        headers = {
            'Authorization':
                b'Basic ' + base64.b64encode(
                    "{}:{}".format(api_key.id, api_key.secret).encode('utf-8'))
        }

        authenticator = OAuthBearerRequestAuthenticator(self.app)
        result = authenticator.authenticate(headers=headers)

        self.assertIsNone(result)

    def test_correct_bearer_api_authentication_fails(self):
        _, acc = self.create_account(self.app.accounts)
        api_key = self.create_api_key(acc)

        headers = {
            'Authorization':
                b'Basic ' + base64.b64encode(
                    "{}:{}".format(api_key.id, api_key.secret).encode('utf-8'))
        }
        body = {'grant_type': 'client_credentials', 'scope': 's1 s2'}
        scopes = ['s1', 's2']

        authenticator = OAuthBearerRequestAuthenticator(self.app)
        result = authenticator.authenticate(
            body=body, headers=headers, scopes=scopes)

        self.assertIsNone(result)

    def test_bearer_api_authentication_without_scopes_and_body_succeeds(self):
        _, acc = self.create_account(self.app.accounts)
        api_key = self.create_api_key(acc)

        headers = {
            'Authorization':
                b'Basic ' + base64.b64encode(
                    "{}:{}".format(api_key.id, api_key.secret).encode('utf-8'))
        }
        uri = 'https://example.com/get?grant_type=client_credentials'

        authenticator = ApiRequestAuthenticator(self.app)
        result = authenticator.authenticate(uri=uri, headers=headers)

        self.assertEqual(api_key.id, result.api_key.id)
        self.assertEqual(api_key.secret, result.api_key.secret)
        self.assertEqual(acc.href, result.api_key.account.href)

        headers = {
            'Authorization': b'Bearer ' + result.token.token.encode('utf-8')}

        authenticator = OAuthBearerRequestAuthenticator(self.app)
        result = authenticator.authenticate(headers=headers)

        self.assertIsNotNone(result)
        self.assertEqual(acc.href, result.account.href)

    def test_basic_api_auth_w_grant_type_in_uri_doesnt_get_token(self):
        _, acc = self.create_account(self.app.accounts)
        api_key = self.create_api_key(acc)

        headers = {
            'Authorization':
                b'Basic ' + base64.b64encode(
                    "{}:{}".format(api_key.id, api_key.secret).encode('utf-8'))
        }
        body = {'scope': 's1 s2'}
        scopes = ['s1', 's2']
        uri = 'https://example.com/get?grant_type=client_credentials'

        authenticator = OAuthBearerRequestAuthenticator(self.app)
        result = authenticator.authenticate(
            uri=uri, body=body, headers=headers, scopes=scopes)

        self.assertIsNone(result)

    def test_bearer_api_authentication_with_unicode_succeeds(self):
        _, acc = self.create_account(self.app.accounts)
        api_key = self.create_api_key(acc)

        b64_key = base64.b64encode(
            '{}:{}'.format(api_key.id, api_key.secret).encode('utf-8'))
        headers = {
            'Authorization': u('Basic ') + b64_key.decode('utf-8')
        }
        body = {'grant_type': 'client_credentials', 'scope': 's1 s2'}
        scopes = ['s1', 's2']

        authenticator = ApiRequestAuthenticator(self.app)
        result = authenticator.authenticate(
            body=body, headers=headers, scopes=scopes)

        self.assertEqual(api_key.id, result.api_key.id)
        self.assertEqual(api_key.secret, result.api_key.secret)
        self.assertEqual(acc.href, result.api_key.account.href)
        self.assertEqual(result.token.scopes, scopes)

        headers = {
            'Authorization': u('Bearer ') + result.token.token}

        authenticator = OAuthBearerRequestAuthenticator(self.app)
        result = authenticator.authenticate(headers=headers, scopes=scopes)

        self.assertIsNotNone(result)
        self.assertEqual(acc.href, result.account.href)

    def test_bearer_api_authentication_with_wrong_token_fails(self):
        headers = {'Authorization': b'Bearer INVALID_TOKEN'}

        authenticator = OAuthBearerRequestAuthenticator(self.app)
        result = authenticator.authenticate(headers=headers)

        self.assertIsNone(result)

    def test_bearer_api_authentication_with_wrong_scope_fails(self):
        _, acc = self.create_account(self.app.accounts)
        api_key = self.create_api_key(acc)

        headers = {
            'Authorization':
                b'Basic ' + base64.b64encode(
                    "{}:{}".format(api_key.id, api_key.secret).encode('utf-8'))
        }
        body = {'grant_type': 'client_credentials', 'scope': 's1'}

        authenticator = ApiRequestAuthenticator(self.app)
        result = authenticator.authenticate(
            body=body, headers=headers, scopes=['s1'])

        self.assertEqual(api_key.id, result.api_key.id)
        self.assertEqual(api_key.secret, result.api_key.secret)
        self.assertEqual(acc.href, result.api_key.account.href)
        self.assertEqual(result.token.scopes, ['s1'])

        headers = {
            'Authorization': b'Bearer ' + result.token.token.encode('utf-8')}

        authenticator = OAuthBearerRequestAuthenticator(self.app)
        result = authenticator.authenticate(
            headers=headers, scopes=['s1', 's2'])

        self.assertIsNone(result)

    def test_valid_bearer_token_but_deleted_api_key(self):
        _, acc = self.create_account(self.app.accounts)
        api_key = self.create_api_key(acc)

        basic_auth = base64.b64encode(
            "{}:{}".format(api_key.id, api_key.secret).encode('utf-8'))

        body = {'grant_type': 'client_credentials', 'scope': 'test1'}
        headers = {
                'Authorization': b'Basic ' + basic_auth
                }

        allowed_scopes = ['test1']

        authenticator = ApiRequestAuthenticator(self.app)
        result = authenticator.authenticate(
            body=body, headers=headers, scopes=allowed_scopes)

        self.assertIsNotNone(result)
        self.assertIsNotNone(result.token)
        token = result.token
        body = {}
        headers = {
                'Authorization': b'Bearer ' + token.token.encode('utf-8')
                }

        api_key.delete()

        authenticator = OAuthBearerRequestAuthenticator(self.app)
        result = authenticator.authenticate(
            headers=headers, scopes=allowed_scopes)

        self.assertIsNone(result)

    def test_valid_bearer_token_but_disabled_api_key(self):
        _, acc = self.create_account(self.app.accounts)
        api_key = self.create_api_key(acc)

        basic_auth = base64.b64encode(
            "{}:{}".format(api_key.id, api_key.secret).encode('utf-8'))

        body = {'grant_type': 'client_credentials', 'scope': 'test1'}
        headers = {
                'Authorization': b'Basic ' + basic_auth
                }

        allowed_scopes = ['test1']

        authenticator = ApiRequestAuthenticator(self.app)
        result = authenticator.authenticate(
            body=body, headers=headers, scopes=allowed_scopes)

        self.assertIsNotNone(result)
        self.assertIsNotNone(result.token)
        token = result.token
        body = {}
        headers = {
                'Authorization': b'Bearer ' + token.token.encode('utf-8')
                }

        api_key.status = 'disabled'
        api_key.save()

        authenticator = OAuthBearerRequestAuthenticator(self.app)
        result = authenticator.authenticate(
            headers=headers, scopes=allowed_scopes)

        self.assertIsNone(result)


class TestApiRequestAuthenticator(ApiKeyBase):

    def test_correct_basic_api_authentication_fails(self):
        _, acc = self.create_account(self.app.accounts)
        api_key = self.create_api_key(acc)

        headers = {
            'Authorization':
                b'Basic ' + base64.b64encode(
                    "{}:{}".format(api_key.id, api_key.secret).encode('utf-8'))
        }

        authenticator = OAuthClientCredentialsRequestAuthenticator(self.app)
        result = authenticator.authenticate(headers=headers)

        self.assertIsNone(result)

    def test_bearer_api_authentication_succeeds_then_fails(self):
        _, acc = self.create_account(self.app.accounts)
        api_key = self.create_api_key(acc)

        headers = {
            'Authorization':
                b'Basic ' + base64.b64encode(
                    "{}:{}".format(api_key.id, api_key.secret).encode('utf-8'))
        }
        body = {'grant_type': 'client_credentials', 'scope': 's1 s2'}
        scopes = ['s1', 's2']

        authenticator = OAuthClientCredentialsRequestAuthenticator(self.app)
        result = authenticator.authenticate(
            body=body, headers=headers, scopes=scopes)

        self.assertEqual(api_key.id, result.api_key.id)
        self.assertEqual(api_key.secret, result.api_key.secret)
        self.assertEqual(acc.href, result.api_key.account.href)
        self.assertEqual(result.token.scopes, scopes)

        headers = {
            'Authorization': b'Bearer ' + result.token.token.encode('utf-8')}

        authenticator = OAuthClientCredentialsRequestAuthenticator(self.app)
        result = authenticator.authenticate(headers=headers, scopes=scopes)

        self.assertIsNone(result)

    def test_bearer_api_authentication_without_scopes_and_body_succeeds(self):
        _, acc = self.create_account(self.app.accounts)
        api_key = self.create_api_key(acc)

        headers = {
            'Authorization':
                b'Basic ' + base64.b64encode(
                    "{}:{}".format(api_key.id, api_key.secret).encode('utf-8'))
        }
        uri = 'https://example.com/get?grant_type=client_credentials'

        authenticator = OAuthClientCredentialsRequestAuthenticator(self.app)
        result = authenticator.authenticate(uri=uri, headers=headers)

        self.assertEqual(api_key.id, result.api_key.id)
        self.assertEqual(api_key.secret, result.api_key.secret)
        self.assertEqual(acc.href, result.api_key.account.href)

        headers = {
            'Authorization': b'Bearer ' + result.token.token.encode('utf-8')}

        authenticator = ApiRequestAuthenticator(self.app)
        result = authenticator.authenticate(headers=headers)

        self.assertIsNotNone(result)
        self.assertEqual(acc.href, result.account.href)

    def test_basic_api_authentication_with_grant_type_in_uri_gets_token(self):
        _, acc = self.create_account(self.app.accounts)
        api_key = self.create_api_key(acc)

        headers = {
            'Authorization':
                b'Basic ' + base64.b64encode(
                    "{}:{}".format(api_key.id, api_key.secret).encode('utf-8'))
        }
        body = {'scope': 's1 s2'}
        scopes = ['s1', 's2']
        uri = 'https://example.com/get?grant_type=client_credentials'

        authenticator = OAuthClientCredentialsRequestAuthenticator(self.app)
        result = authenticator.authenticate(
            uri=uri, body=body, headers=headers, scopes=scopes)

        self.assertIsNotNone(result.token)
        self.assertEqual(result.token.scopes, scopes)

    def test_basic_api_auth_w_wrong_grant_type_in_uri_does_not_get_token(self):
        _, acc = self.create_account(self.app.accounts)
        api_key = self.create_api_key(acc)

        headers = {
            'Authorization':
                b'Basic ' + base64.b64encode(
                    "{}:{}".format(api_key.id, api_key.secret).encode('utf-8'))
        }
        body = {'scope': 's1 s2'}
        scopes = ['s1', 's2']
        uri = 'https://example.com/get?grant_type=invalid_grant_type'

        authenticator = OAuthClientCredentialsRequestAuthenticator(self.app)
        result = authenticator.authenticate(
            uri=uri, body=body, headers=headers, scopes=scopes)

        self.assertIsNone(result.token)

    def test_bearer_api_authentication_with_unicode_succeeds(self):
        _, acc = self.create_account(self.app.accounts)
        api_key = self.create_api_key(acc)

        b64_key = base64.b64encode(
            '{}:{}'.format(api_key.id, api_key.secret).encode('utf-8'))
        headers = {
            'Authorization': u('Basic ') + b64_key.decode('utf-8')
        }
        body = {'grant_type': 'client_credentials', 'scope': 's1 s2'}
        scopes = ['s1', 's2']

        authenticator = OAuthClientCredentialsRequestAuthenticator(self.app)
        result = authenticator.authenticate(
            body=body, headers=headers, scopes=scopes)

        self.assertEqual(api_key.id, result.api_key.id)
        self.assertEqual(api_key.secret, result.api_key.secret)
        self.assertEqual(acc.href, result.api_key.account.href)
        self.assertEqual(result.token.scopes, scopes)

        headers = {
            'Authorization': u('Bearer ') + result.token.token}

        authenticator = ApiRequestAuthenticator(self.app)
        result = authenticator.authenticate(headers=headers, scopes=scopes)

        self.assertIsNotNone(result)
        self.assertEqual(acc.href, result.account.href)

    def test_bearer_api_authentication_with_wrong_scope_fails(self):
        _, acc = self.create_account(self.app.accounts)
        api_key = self.create_api_key(acc)

        headers = {
            'Authorization':
                b'Basic ' + base64.b64encode(
                    "{}:{}".format(api_key.id, api_key.secret).encode('utf-8'))
        }
        body = {'grant_type': 'client_credentials', 'scope': 's1'}

        authenticator = OAuthClientCredentialsRequestAuthenticator(self.app)
        result = authenticator.authenticate(
            body=body, headers=headers, scopes=['s1'])

        self.assertEqual(api_key.id, result.api_key.id)
        self.assertEqual(api_key.secret, result.api_key.secret)
        self.assertEqual(acc.href, result.api_key.account.href)
        self.assertEqual(result.token.scopes, ['s1'])

        headers = {
            'Authorization': b'Bearer ' + result.token.token.encode('utf-8')}

        authenticator = ApiRequestAuthenticator(self.app)
        result = authenticator.authenticate(
            headers=headers, scopes=['s1', 's2'])

        self.assertIsNone(result)

    def test_valid_bearer_token_but_deleted_api_key(self):
        _, acc = self.create_account(self.app.accounts)
        api_key = self.create_api_key(acc)

        basic_auth = base64.b64encode(
            "{}:{}".format(api_key.id, api_key.secret).encode('utf-8'))

        body = {'grant_type': 'client_credentials', 'scope': 'test1'}
        headers = {
                'Authorization': b'Basic ' + basic_auth
                }

        allowed_scopes = ['test1']

        authenticator = OAuthClientCredentialsRequestAuthenticator(self.app)
        result = authenticator.authenticate(
            body=body, headers=headers, scopes=allowed_scopes)

        self.assertIsNotNone(result)
        self.assertIsNotNone(result.token)
        token = result.token
        body = {}
        headers = {
                'Authorization': b'Bearer ' + token.token.encode('utf-8')
                }

        api_key.delete()

        authenticator = ApiRequestAuthenticator(self.app)
        result = authenticator.authenticate(
            headers=headers, scopes=allowed_scopes)

        self.assertIsNone(result)

    def test_valid_bearer_token_but_disabled_api_key(self):
        _, acc = self.create_account(self.app.accounts)
        api_key = self.create_api_key(acc)

        basic_auth = base64.b64encode(
            "{}:{}".format(api_key.id, api_key.secret).encode('utf-8'))

        body = {'grant_type': 'client_credentials', 'scope': 'test1'}
        headers = {
                'Authorization': b'Basic ' + basic_auth
                }

        allowed_scopes = ['test1']

        authenticator = OAuthClientCredentialsRequestAuthenticator(self.app)
        result = authenticator.authenticate(
            body=body, headers=headers, scopes=allowed_scopes)

        self.assertIsNotNone(result)
        self.assertIsNotNone(result.token)
        token = result.token
        body = {}
        headers = {
                'Authorization': b'Bearer ' + token.token.encode('utf-8')
                }

        api_key.status = 'disabled'
        api_key.save()

        authenticator = ApiRequestAuthenticator(self.app)
        result = authenticator.authenticate(
            headers=headers, scopes=allowed_scopes)

        self.assertIsNone(result)

    def test_invalid_grant_type_no_token_gets_generated(self):
        _, acc = self.create_account(self.app.accounts)
        api_key = self.create_api_key(acc)

        basic_auth = base64.b64encode(
            "{}:{}".format(api_key.id, api_key.secret).encode('utf-8'))

        body = {'grant_type': 'invalid_grant', 'scope': 'test1'}
        headers = {
                'Authorization': b'Basic ' + basic_auth
                }

        allowed_scopes = ['test1']

        authenticator = OAuthClientCredentialsRequestAuthenticator(self.app)
        result = authenticator.authenticate(
            body=body, headers=headers, scopes=allowed_scopes)

        self.assertIsNotNone(result)
        self.assertIsNone(result.token)


class TestPasswordGrantAuthenticator(ApiKeyBase):

    def setUp(self):
        super(TestPasswordGrantAuthenticator, self).setUp()

        self.username = self.get_random_name()
        self.password = 'W00t123!' + self.username
        _, self.acc = self.create_account(
            self.app.accounts, username=self.username, password=self.password)

    def test_authenticate_succeeds(self):
        authenticator = PasswordGrantAuthenticator(self.app)
        result = authenticator.authenticate(self.username, self.password)

        self.assertTrue(result.access_token)
        self.assertTrue(result.refresh_token)
        self.assertTrue(result.stormpath_access_token)
        self.assertEqual(result.token_type, 'Bearer')
        self.assertTrue(result.refresh_token)
        self.assertEqual(result.expires_in, 3600)
        self.assertEqual(result.account.href, self.acc.href)

    def test_authenticate_fails(self):
        authenticator = PasswordGrantAuthenticator(self.app)
        result = authenticator.authenticate(self.username, 'invalid')

        self.assertIsNone(result)

    def test_authenticate_with_account_store_succeeds(self):
        authenticator = PasswordGrantAuthenticator(self.app)
        result = authenticator.authenticate(
            self.username, self.password, account_store=self.dir)

        self.assertTrue(result.access_token)
        self.assertTrue(result.refresh_token)
        self.assertEqual(result.account.href, self.acc.href)
        self.assertTrue('access_token' in result.access_token.to_json())
        self.assertTrue('refresh_token' in result.refresh_token.to_json())
        self.assertTrue(hasattr(result.stormpath_access_token, 'href'))
        self.assertEqual(
            result.stormpath_access_token.account.href, self.acc.href)
        self.assertEqual(result.token_type, 'Bearer')
        self.assertEqual(result.expires_in, 3600)
        self.assertEqual(result.account.href, self.acc.href)

    def test_authenticate_with_account_store_fails(self):
        authenticator = PasswordGrantAuthenticator(self.app)
        result = authenticator.authenticate(
            self.username, 'invalid', account_store=self.dir)

        self.assertIsNone(result)

    def test_authenticate_with_account_store_href_succeeds(self):
        authenticator = PasswordGrantAuthenticator(self.app)
        result = authenticator.authenticate(
            self.username, self.password, account_store=self.dir.href)

        self.assertTrue(result.access_token)
        self.assertTrue(result.refresh_token)
        self.assertEqual(result.account.href, self.acc.href)
        self.assertTrue('access_token' in result.access_token.to_json())
        self.assertTrue('refresh_token' in result.refresh_token.to_json())
        self.assertTrue(hasattr(result.stormpath_access_token, 'href'))
        self.assertEqual(
            result.stormpath_access_token.account.href, self.acc.href)
        self.assertEqual(result.token_type, 'Bearer')
        self.assertEqual(result.expires_in, 3600)
        self.assertEqual(result.account.href, self.acc.href)


class TestJwtAuthenticator(ApiKeyBase):

    def setUp(self):
        super(TestJwtAuthenticator, self).setUp()

        self.username = self.get_random_name()
        self.password = 'W00t123!' + self.username
        _, self.acc = self.create_account(
            self.app.accounts, username=self.username, password=self.password)

        self.access_token_ttl_seconds = 5
        self.app.oauth_policy.access_token_ttl = datetime.timedelta(
            seconds=self.access_token_ttl_seconds)
        self.app.oauth_policy.save()
        pg_auth = PasswordGrantAuthenticator(self.app)
        pg_auth_result = pg_auth.authenticate(self.username, self.password)
        self.access_token = pg_auth_result.access_token

        app2_name = self.get_random_name()
        self.app2 = self.client.applications.create({
            'name': app2_name,
            'description': 'test app'
        }, create_directory=app2_name)

    def tearDown(self):
        super(TestJwtAuthenticator, self).tearDown()
        self.app2.delete()

    def test_authenticate_succeeds(self):
        authenticator = JwtAuthenticator(self.app)
        result = authenticator.authenticate(self.access_token.token)

        self.assertIsInstance(result, AuthToken)
        self.assertEqual(result.account.href, self.acc.href)
        self.assertEqual(result.application.href, self.app.href)
        self.assertEqual(result.jwt, self.access_token.token)
        self.assertTrue('claims' in result.expanded_jwt)

    def test_authenticate_with_expansion_succeeds(self):
        authenticator = JwtAuthenticator(self.app)
        expansion = Expansion()
        expansion.add_property('account')
        result = authenticator.authenticate(
            self.access_token.token, expand=expansion)

        self.assertIsInstance(result, AuthToken)
        self.assertEqual(result.account.href, self.acc.href)
        self.assertEqual(result.application.href, self.app.href)
        self.assertEqual(result.jwt, self.access_token.token)
        self.assertTrue('claims' in result.expanded_jwt)

    def test_authenticate_invalid_jwt_fails(self):
        authenticator = JwtAuthenticator(self.app)
        result = authenticator.authenticate('invalid_token')

        self.assertIsNone(result)

    def test_authenticate_invalid_app_fails(self):
        authenticator = JwtAuthenticator(self.app2)
        result = authenticator.authenticate(self.access_token.token)

        self.assertIsNone(result)

    def test_authenticate_expired_fails(self):
        authenticator = JwtAuthenticator(self.app)
        sleep(self.access_token_ttl_seconds)
        result = authenticator.authenticate(self.access_token.token)

        self.assertIsNone(result)

    def test_authenticate_revoked_fails(self):
        # get access token
        authenticator = JwtAuthenticator(self.app)
        stormpath_access_token = authenticator.authenticate(self.access_token)
        token = stormpath_access_token.jwt

        # revoke access token
        stormpath_access_token.delete()

        # try to authenticate again
        result = authenticator.authenticate(token)

        self.assertIsNone(result)

    def test_authenticate_with_local_validation_succeeds(self):
        authenticator = JwtAuthenticator(self.app)
        result = authenticator.authenticate(
            self.access_token.token, local_validation=True)

        self.assertIsInstance(result, AccessToken)
        self.assertEqual(result.account.href, self.acc.href)
        self.assertEqual(result.app.href, self.app.href)
        self.assertEqual(result.token, self.access_token.token)

    def test_authenticate_with_local_validation_invalid_token_fails(self):
        authenticator = JwtAuthenticator(self.app)
        result = authenticator.authenticate(
            'invalid_token', local_validation=True)

        self.assertIsNone(result)

    def test_authenticate_with_local_validation_invalid_app_fails(self):
        authenticator = JwtAuthenticator(self.app2)
        result = authenticator.authenticate(
            self.access_token.token, local_validation=True)

        self.assertIsNone(result)

    def test_authenticate_with_local_validation_expired_fails(self):
        authenticator = JwtAuthenticator(self.app)
        sleep(self.access_token_ttl_seconds)
        result = authenticator.authenticate(
            self.access_token.token, local_validation=True)

        self.assertIsNone(result)

    def test_authenticate_with_local_validation_revoked_succeeds(self):
        # get access token
        authenticator = JwtAuthenticator(self.app)
        stormpath_access_token = authenticator.authenticate(self.access_token)
        token = stormpath_access_token.jwt

        # revoke access token
        stormpath_access_token.delete()

        # try to authenticate again
        result = authenticator.authenticate(token, local_validation=True)

        self.assertIsInstance(result, AccessToken)
        self.assertEqual(result.account.href, self.acc.href)
        self.assertEqual(result.app.href, self.app.href)
        self.assertEqual(result.token, self.access_token.token)


class TestRefreshGrantAuthenticator(ApiKeyBase):

    def setUp(self):
        super(TestRefreshGrantAuthenticator, self).setUp()

        self.username = self.get_random_name()
        self.password = 'W00t123!' + self.username
        _, self.acc = self.create_account(
            self.app.accounts, username=self.username, password=self.password)

        self.access_token_ttl_seconds = 5
        self.refresh_token_ttl_seconds = 10
        self.app.oauth_policy.access_token_ttl = datetime.timedelta(
            seconds=self.access_token_ttl_seconds)
        self.app.oauth_policy.refresh_token_ttl = datetime.timedelta(
            seconds=self.refresh_token_ttl_seconds)
        self.app.oauth_policy.save()
        pg_auth = PasswordGrantAuthenticator(self.app)
        pg_auth_result = pg_auth.authenticate(self.username, self.password)
        self.access_token = pg_auth_result.access_token
        self.refresh_token = pg_auth_result.refresh_token

        app2_name = self.get_random_name()
        self.app2 = self.client.applications.create({
            'name': app2_name,
            'description': 'test app'
        }, create_directory=app2_name)

    def tearDown(self):
        super(TestRefreshGrantAuthenticator, self).tearDown()
        self.app2.delete()

    def test_authenticate_succeeds(self):
        # access token expires
        sleep(self.access_token_ttl_seconds)
        authenticator = JwtAuthenticator(self.app)
        result = authenticator.authenticate(self.access_token.token)

        self.assertIsNone(result)

        # we refresh access token
        authenticator = RefreshGrantAuthenticator(self.app)
        result = authenticator.authenticate(self.refresh_token)

        self.assertTrue(result.access_token)
        self.assertTrue(result.refresh_token)
        self.assertEqual(result.account.href, self.acc.href)
        self.assertTrue('access_token' in result.access_token.to_json())
        self.assertTrue('refresh_token' in result.refresh_token.to_json())
        self.assertTrue(hasattr(result.stormpath_access_token, 'href'))
        self.assertEqual(
            result.stormpath_access_token.account.href, self.acc.href)
        self.assertEqual(result.token_type, 'Bearer')
        self.assertEqual(result.expires_in, self.access_token_ttl_seconds)
        self.assertEqual(result.account.href, self.acc.href)

        # new access token is valid
        authenticator = JwtAuthenticator(self.app)
        result = authenticator.authenticate(result.access_token.token)

        self.assertIsInstance(result, AuthToken)
        self.assertEqual(result.account.href, self.acc.href)
        self.assertEqual(result.application.href, self.app.href)
        self.assertNotEqual(result.jwt, self.access_token.token)
        self.assertTrue('claims' in result.expanded_jwt)

    def test_authenticate_with_token_string_succeeds(self):
        authenticator = RefreshGrantAuthenticator(self.app)
        result = authenticator.authenticate(self.refresh_token.token)

        self.assertTrue(result.access_token)
        self.assertTrue(result.refresh_token)
        self.assertEqual(result.account.href, self.acc.href)
        self.assertTrue('access_token' in result.access_token.to_json())
        self.assertTrue('refresh_token' in result.refresh_token.to_json())
        self.assertTrue(hasattr(result.stormpath_access_token, 'href'))
        self.assertEqual(
            result.stormpath_access_token.account.href, self.acc.href)
        self.assertEqual(result.token_type, 'Bearer')
        self.assertEqual(result.expires_in, self.access_token_ttl_seconds)
        self.assertEqual(result.account.href, self.acc.href)

    def test_authenticate_with_access_token_fails(self):
        authenticator = RefreshGrantAuthenticator(self.app)
        result = authenticator.authenticate(self.access_token.token)

        self.assertIsNone(result)

    def test_authenticate_with_invalid_app_fails(self):
        authenticator = RefreshGrantAuthenticator(self.app2)
        result = authenticator.authenticate(self.refresh_token.token)

        self.assertIsNone(result)

    def test_authenticate_with_expired_refresh_token_fails(self):
        # both access and refresh token expire
        sleep(self.refresh_token_ttl_seconds)
        authenticator = JwtAuthenticator(self.app)
        result = authenticator.authenticate(self.access_token.token)

        self.assertIsNone(result)

        # we try to refresh access token
        authenticator = RefreshGrantAuthenticator(self.app)
        result = authenticator.authenticate(self.refresh_token)

        self.assertIsNone(result)

    def test_authenticate_with_revoked_refresh_token_fails(self):
        # we revoke refresh token
        token = self.refresh_token.token
        stormpath_refresh_token = self.app.auth_tokens.get(token)
        print stormpath_refresh_token.jwt
        stormpath_refresh_token.delete()

        # access token expires
        sleep(self.access_token_ttl_seconds)
        authenticator = JwtAuthenticator(self.app)
        result = authenticator.authenticate(self.access_token.token)

        self.assertIsNone(result)

        # we try to refresh access token
        authenticator = RefreshGrantAuthenticator(self.app)
        result = authenticator.authenticate(token)

        self.assertIsNone(result)

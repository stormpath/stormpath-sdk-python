"""Live tests of client authentication against the Stormpath service API."""
import base64
from six import u

from .base import ApiKeyBase
from stormpath.api_auth import *
from stormpath.error import Error as StormpathError


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

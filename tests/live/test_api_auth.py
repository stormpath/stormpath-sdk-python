"""Live tests of client authentication against the Stormpath service API."""
import base64
from six import u

from .base import ApiKeyBase


class TestApiAuth(ApiKeyBase):

    def test_basic_api_authentication_succeeds(self):
        _, acc = self.create_account(self.app.accounts)
        api_key = self.create_api_key(acc)

        headers = {
            'Authorization':
                b'Basic ' + base64.b64encode(
                    "{}:{}".format(api_key.id, api_key.secret).encode('utf-8'))
        }

        result = self.app.authenticate_api(body={}, headers=headers)

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

        result = self.app.authenticate_api(body={}, headers=headers)

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

        result = self.app.authenticate_api(body={}, headers=headers)

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

        result = self.app.authenticate_api(
            allowed_scopes=scopes, body=body, headers=headers)

        self.assertEqual(api_key.id, result.api_key.id)
        self.assertEqual(api_key.secret, result.api_key.secret)
        self.assertEqual(acc.href, result.api_key.account.href)
        self.assertEqual(result.token.scopes, scopes)

        headers = {
            'Authorization': b'Bearer ' + result.token.token.encode('utf-8')}

        result = self.app.authenticate_api(
            allowed_scopes=scopes, body={}, headers=headers)

        self.assertIsNotNone(result)
        self.assertEqual(acc.href, result.account.href)

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

        result = self.app.authenticate_api(
            allowed_scopes=scopes, body=body, headers=headers)

        self.assertEqual(api_key.id, result.api_key.id)
        self.assertEqual(api_key.secret, result.api_key.secret)
        self.assertEqual(acc.href, result.api_key.account.href)
        self.assertEqual(result.token.scopes, scopes)

        headers = {
            'Authorization': u('Bearer ') + result.token.token}

        result = self.app.authenticate_api(
            allowed_scopes=scopes, body={}, headers=headers)

        self.assertIsNotNone(result)
        self.assertEqual(acc.href, result.account.href)

    def test_bearer_api_authentication_with_wrong_token_fails(self):
        headers = {'Authorization': b'Bearer INVALID_TOKEN'}

        result = self.app.authenticate_api(
            allowed_scopes=[], body={}, headers=headers)

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

        result = self.app.authenticate_api(
            allowed_scopes=['s1'], body=body, headers=headers)

        self.assertEqual(api_key.id, result.api_key.id)
        self.assertEqual(api_key.secret, result.api_key.secret)
        self.assertEqual(acc.href, result.api_key.account.href)
        self.assertEqual(result.token.scopes, ['s1'])

        headers = {
            'Authorization': b'Bearer ' + result.token.token.encode('utf-8')}

        result = self.app.authenticate_api(
            allowed_scopes=['s1', 's2'], body={}, headers=headers)

        self.assertIsNone(result)

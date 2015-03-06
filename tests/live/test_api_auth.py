"""Live tests of client authentication against the Stormpath service API."""
import base64
from six import u

from .base import ApiKeyBase
from stormpath.error import Error as StormpathError


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

        result = self.app.authenticate_api(
            allowed_scopes=allowed_scopes, body=body, headers=headers)
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.token)
        token = result.token
        body = {}
        headers = {
                'Authorization': b'Bearer ' + token.token.encode('utf-8')
                }

        api_key.delete()

        result = self.app.authenticate_api(
            allowed_scopes=allowed_scopes, body=body, headers=headers)
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

        result = self.app.authenticate_api(
            allowed_scopes=allowed_scopes, body=body, headers=headers)
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.token)
        token = result.token
        body = {}
        headers = {
                'Authorization': b'Bearer ' + token.token.encode('utf-8')
                }

        api_key.status = 'disabled'
        api_key.save()

        result = self.app.authenticate_api(
            allowed_scopes=allowed_scopes, body=body, headers=headers)
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

        result = self.app.authenticate_api(
            allowed_scopes=allowed_scopes, body=body, headers=headers)
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

        result = self.app.authenticate_api(body={}, headers=headers)
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

        result = self.app.authenticate_api(body={}, headers=headers)
        self.assertIsNone(result)

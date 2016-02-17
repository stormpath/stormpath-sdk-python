from uuid import uuid4
import datetime
import jwt
from oauthlib.common import to_unicode

from unittest import TestCase
try:
    from mock import create_autospec, MagicMock, patch
except ImportError:
    from unittest.mock import create_autospec, MagicMock, patch

from stormpath.resources.application import (
    Application, ApplicationList, StormpathCallbackResult
)


class IDSiteBuildURITest(TestCase):

    def setUp(self):
        self.client = MagicMock(BASE_URL='')
        self.client.auth = MagicMock()
        self.client.auth.id = 'ID'
        self.client.auth.secret = 'SECRET'


    def test_building_id_site_redirect_uri(self):
        try:
            from urlparse import urlparse
        except ImportError:
            from urllib.parse import urlparse

        app = Application(client=self.client, properties={'href': 'apphref'})

        ret = app.build_id_site_redirect_url('http://localhost/')
        try:
            jwt_response = urlparse(ret).query.split('=')[1]
        except:
            self.fail("Failed to parse ID site redirect uri")

        try:
            decoded_data = jwt.decode(
                jwt_response, verify=False, algorithms=['HS256'])
        except jwt.DecodeError:
            self.fail("Invaid JWT generated.")

        self.assertIsNotNone(decoded_data.get('iat'))
        self.assertIsNotNone(decoded_data.get('jti'))
        self.assertIsNotNone(decoded_data.get('iss'))
        self.assertIsNotNone(decoded_data.get('sub'))
        self.assertIsNotNone(decoded_data.get('cb_uri'))
        self.assertEqual(decoded_data.get('cb_uri'), 'http://localhost/')
        self.assertIsNone(decoded_data.get('path'))
        self.assertIsNone(decoded_data.get('state'))

        ret = app.build_id_site_redirect_url(
                'http://testserver/',
                path='/#/register',
                state='test')
        try:
            jwt_response = urlparse(ret).query.split('=')[1]
        except:
            self.fail("Failed to parse ID site redirect uri")

        try:
            decoded_data = jwt.decode(
                jwt_response, verify=False, algorithms=['HS256'])
        except jwt.DecodeError:
            self.fail("Invaid JWT generated.")

        self.assertEqual(decoded_data.get('path'), '/#/register')
        self.assertEqual(decoded_data.get('state'), 'test')


class IDSiteCallbackTest(IDSiteBuildURITest):

    def setUp(self):
        super(IDSiteCallbackTest, self).setUp()
        self.store = MagicMock()
        self.store.get_resource.return_value = {
            'href': 'acchref',
            'sp_http_status': 200,
            'applications': ApplicationList(
                client=self.client,
                properties={
                    'href': 'apps',
                    'items': [{'href': 'apphref'}],
                    'offset': 0,
                    'limit': 25
                })
        }
        self.store._cache_get.return_value = False # ignore nonce

        self.client.data_store = self.store

        self.app = Application(
                client=self.client,
                properties={'href': 'apphref', 'accounts': {'href': 'acchref'}})

        self.acc = MagicMock(href='acchref')
        now = datetime.datetime.utcnow()

        try:
            irt = uuid4().get_hex()
        except AttributeError:
            irt = uuid4().hex

        fake_jwt_data = {
                'exp': now + datetime.timedelta(seconds=3600),
                'aud': self.app._client.auth.id,
                'irt': irt,
                'iss': 'Stormpath',
                'sub': self.acc.href,
                'isNewSub': False,
                'state': None,
        }

        self.fake_jwt = to_unicode(jwt.encode(
            fake_jwt_data,
            self.app._client.auth.secret,
            'HS256'), 'UTF-8')

    def test_id_site_callback_handler(self):
        fake_jwt_response = 'http://localhost/?jwtResponse=%s' % self.fake_jwt

        with patch.object(Application, 'has_account') as mock_has_account:
            mock_has_account.return_value = True
            ret = self.app.handle_stormpath_callback(fake_jwt_response)

        self.assertIsNotNone(ret)
        self.assertIsInstance(ret, StormpathCallbackResult)
        self.assertEqual(ret.account.href, self.acc.href)
        self.assertIsNone(ret.state)

    def test_id_site_callback_handler_jwt_already_used(self):
        self.store._cache_get.return_value = True # Fake Nonce already used

        fake_jwt_response = 'http://localhost/?jwtResponse=%s' % self.fake_jwt
        self.assertRaises(
            ValueError, self.app.handle_stormpath_callback, fake_jwt_response)

    def test_id_site_callback_handler_invalid_jwt(self):
        fake_jwt_response = 'http://localhost/?jwtResponse=%s' % 'INVALID_JWT'
        ret = self.app.handle_stormpath_callback(fake_jwt_response)
        self.assertIsNone(ret)

    def test_id_site_callback_handler_invalid_url_response(self):
        fake_jwt_response = 'invalid_url_response'
        ret = self.app.handle_stormpath_callback(fake_jwt_response)
        self.assertIsNone(ret)

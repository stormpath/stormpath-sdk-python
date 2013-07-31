from unittest import TestCase, main
from stormpath.auth import Auth, Sauthc1Signer

from mock import patch, Mock, MagicMock
import datetime


class AuthTest(TestCase):

    @patch.object(Auth, '_load_properties')
    def test_auth_key_file_parsing(self, _load_properties):
        _load_properties.return_value = {
            'apiKey.id': 'MyId',
            'apiKey.secret': 'Shush!'
        }
        mock_isfile = MagicMock(return_value=True)

        with patch('stormpath.auth.isfile', mock_isfile):
            a = Auth(api_key_file_location='apiKey.properties')
        self.assertEqual(a.id, 'MyId')
        self.assertEqual(a.secret, 'Shush!')

    def test_auth_key_dict(self):
        a = Auth(api_key={'id': 'MyId', 'secret': 'Shush!'})

        self.assertEqual(a.id, 'MyId')
        self.assertEqual(a.secret, 'Shush!')

    def test_set_id_secret_directly(self):
        a = Auth(id='MyId', secret='Shush!')

        self.assertEqual(a.id, 'MyId')
        self.assertEqual(a.secret, 'Shush!')

    def test_sauthc1signer(self):
        r = MagicMock()
        r.headers = {}
        r.url = 'https://api.stormpath.com/v1/'
        r.method = 'GET'
        r.body = None

        mock_dt = MagicMock()
        mock_dt.utcnow.return_value = datetime.datetime(2013, 7, 1,
            0, 0, 0, 0)
        mock_uuid4 = MagicMock(
            return_value='a43a9d25-ab06-421e-8605-33fd1e760825')
        s = Sauthc1Signer(id='MyId', secret='Shush!')
        with patch('stormpath.auth.datetime', mock_dt):
            with patch('stormpath.auth.uuid4', mock_uuid4):
                r2 = s(r)

        self.assertEqual(r, r2)
        self.assertEqual(r.headers['Authorization'],
            'SAuthc1 sauthc1Id=MyId/20130701/a43a9d25-ab06-421e-8605-33fd1e760825/sauthc1_request, ' +  # noqa
            'sauthc1SignedHeaders=host;x-stormpath-date, ' +
            'sauthc1Signature=990a95aabbcbeb53e48fb721f73b75bd3ae025a2e86ad359d08558e1bbb9411c')  # noqa

if __name__ == '__main__':
    main()

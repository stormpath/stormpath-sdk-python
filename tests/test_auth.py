from unittest import TestCase
from stormpath.auth import Auth, Sauthc1Signer

from mock import patch, Mock, MagicMock
import datetime


class AuthTest(TestCase):

    def test_auth_key_file_parsing(self):
        mock_fp = MagicMock(spec=file)
        # mocking depends on the jprops internals (iterating through fp
        # context manager to get the lines) - can't be helped :(
        mock_fp.__enter__.return_value.__iter__.return_value = [
            'apiKey.id=MyId\n',
            'apiKey.secret=Shush!\n']
        mock_open = Mock()
        mock_open.return_value = mock_fp
        mock_isfile = MagicMock(return_value=True)

        with patch('stormpath.auth.open', mock_open, create=True):
            with patch('stormpath.auth.isfile', mock_isfile):
                a = Auth(api_key_file_location='apiKey.properties')

        mock_open.assert_called_once_with('apiKey.properties', 'rb')

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

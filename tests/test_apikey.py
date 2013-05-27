import os
import unittest
try:
    from unittest import mock
except ImportError:
    import mock

from stormpath.clients import Client
from stormpath.api_key import ApiKey


class TestApiKey(unittest.TestCase):
    def jprops(self, *args):
        return {
            'apiKey.id': '2GOC9ROK2X65D46TDOJZS4W92',
            'apiKey.secret': 'vvcLLmoCoE+BsA8Xg2Xz2SlglfgWloyWvx56TQfmxpY'}

    def setUp(self):
        self.file_location = os.path.join(os.path.dirname(__file__),
            'apiKey.properties')
        self.id = '2GOC9ROK2X65D46TDOJZS4W92'
        self.secret = 'vvcLLmoCoE+BsA8Xg2Xz2SlglfgWloyWvx56TQfmxpY'

    @mock.patch('stormpath.clients.jprops.load_properties', jprops)
    def test_file_argument(self):
        """
        To test the file argument, create the appropriate apiKey.properties file
        and set the correct file_location. Since the test uses mock to patch
        the function that loads the properties, the file can be empty as long as
        it exists.
        """
        client = Client(api_key_file_location=self.file_location)
        self.assertEqual(client.api_key.id, self.id)
        self.assertEqual(client.api_key.secret, self.secret)

    def test_dict_argument(self):
        client = Client(api_key={'id': self.id, 'secret': self.secret})
        self.assertEqual(client.api_key.id, self.id)
        self.assertEqual(client.api_key.secret, self.secret)

    def test_object_argument(self):
        api_key = ApiKey(self.id, self.secret)
        client = Client(api_key=api_key)
        self.assertEqual(client.api_key.id, self.id)
        self.assertEqual(client.api_key.secret, self.secret)

if __name__ == '__main__':
    unittest.main()

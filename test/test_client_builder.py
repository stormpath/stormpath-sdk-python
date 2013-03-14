__author__ = 'ecrisostomo'

from test.test_base import BaseClientBuilder
from stormpath.client import ClientBuilder, Client

class ClientBuilderTest(BaseClientBuilder):

    def test_default_properties_from_local_file(self):

        result = ClientBuilder().set_api_key_file_location(self.api_key_file).build()

        self.assertIsInstance(result, Client)

    def test_default_properties_from_local_file_fail(self):
        with self.assertRaises(IOError):
            ClientBuilder().set_api_key_file_location('wrongfile').build()

    def test_custom_properties_from_local_file(self):

        result = ClientBuilder().\
                set_api_key_file_location(self.api_key_file).\
                set_api_key_id_property_name('different.apiKey.id').\
                set_api_key_secret_property_name('different.apiKey.secret').\
                build()

        self.assertIsInstance(result, Client)


    def test_custom_properties_from_local_file_fail(self):

        with self.assertRaises(ValueError):
            ClientBuilder().\
            set_api_key_file_location(self.api_key_file).\
            set_api_key_id_property_name('wrongId').\
            build()

    def test_empty_custom_properties_from_local_file(self):

        with self.assertRaises(ValueError):
            ClientBuilder().\
            set_api_key_file_location(self.api_key_file).\
            set_api_key_id_property_name('empty.apiKey.id').\
            build()

    def test_default_properties_from_string(self):
        # getting the YAML content from file...just to avoid writing them directly
        # in the 'properties' string
        with open(self.api_key_file) as f:
            properties = f.read()

        result = ClientBuilder().set_api_key_properties(properties).build()

        self.assertIsInstance(result, Client)

    def test_default_properties_from_string_fail(self):

        with self.assertRaises(ValueError):
            ClientBuilder().set_api_key_properties('bad').build()


    def test_custom_properties_from_string(self):
        # getting the YAML content from file...just to avoid writing them directly
        # in the 'properties' string
        with open(self.api_key_file) as f:
            properties = f.read()

        result = ClientBuilder().set_api_key_properties(properties).\
                 set_api_key_id_property_name('different.apiKey.id').\
                 set_api_key_secret_property_name('different.apiKey.secret').\
                 build()

        self.assertIsInstance(result, Client)

    def test_custom_complex_properties_from_local_file(self):

        result = ClientBuilder().\
                 set_api_key_file_location(self.api_key_file).\
                 set_api_key_id_property_name('stormpath', 'apiKey', 'id').\
                 set_api_key_secret_property_name('stormpath', 'apiKey', 'secret').\
                 build()

        self.assertIsInstance(result, Client)

    def test_custom_complex_properties_from_string(self):
        # getting the YAML content from file...just to avoid writing them directly
        # in the 'properties' string
        with open(self.api_key_file) as f:
                properties = f.read()

        result = ClientBuilder().set_api_key_properties(properties).\
                 set_api_key_id_property_name('stormpath', 'apiKey', 'id').\
                 set_api_key_secret_property_name('stormpath', 'apiKey', 'secret').\
                 build()

        self.assertIsInstance(result, Client)

    def test_custom_complex_properties_from_local_file_fail(self):

        with self.assertRaises(ValueError):
            ClientBuilder().\
            set_api_key_file_location(self.api_key_file).\
            set_api_key_id_property_name('stormpath', 'apiKey').\
            set_api_key_secret_property_name('stormpath', 'apiKey', 'secret').\
            build()

    def test_default_properties_from_remote_file(self):

        result = ClientBuilder().set_api_key_file_location(self.ap_key_remote_file).build()

        self.assertIsInstance(result, Client)

    def test_custom_properties_from_remote_file(self):

        result = ClientBuilder().\
                set_api_key_file_location(self.ap_key_remote_file).\
                set_api_key_id_property_name('different.apiKey.id').\
                set_api_key_secret_property_name('different.apiKey.secret').\
                build()

        self.assertIsInstance(result, Client)


    def test_custom_properties_from_remote_file_fail(self):

        with self.assertRaises(ValueError):
            ClientBuilder().\
            set_api_key_file_location(self.ap_key_remote_file).\
            set_api_key_id_property_name('wrongId').\
            build()

    def test_empty_custom_properties_from_remote_file(self):

        with self.assertRaises(ValueError):
            ClientBuilder().\
            set_api_key_file_location(self.ap_key_remote_file).\
            set_api_key_id_property_name('empty.apiKey.id').\
            build()

    def test_custom_complex_properties_from_remote_file(self):

        result = ClientBuilder().\
                 set_api_key_file_location(self.ap_key_remote_file).\
                 set_api_key_id_property_name('stormpath', 'apiKey', 'id').\
                 set_api_key_secret_property_name('stormpath', 'apiKey', 'secret').\
                 build()

        self.assertIsInstance(result, Client)
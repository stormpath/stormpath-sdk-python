__author__ = 'ecrisostomo'

import yaml
from test.test_base import BaseClientBuilder
from stormpath.client import ClientBuilder, ClientApplicationBuilder
from stormpath.resource import Application

class ClientApplicationBuilderTest(BaseClientBuilder):

    def setUp(self):
        super().setUp()
        self.application_href = 'http://localhost:8080/v1/applications/ys-NzadoQaelH2rDF03VuQ'
        self.http_prefix = 'http://'
        self.app_href_without_http = '@localhost:8080/v1/applications/ys-NzadoQaelH2rDF03VuQ'
        self.client_builder = ClientBuilder().set_base_url('http://localhost:8080/v1').set_api_key_file_location(self.api_key_file)

    def test_default_properties_from_file(self):

        result = ClientApplicationBuilder().\
                 set_application_href(self.application_href).\
                 set_api_key_file_location(self.api_key_file).\
                 build().\
                 application

        self.assertIsInstance(result, Application)

    def test_from_application_href_with_credentials(self):

        # getting the YAML content from file...just to avoid writing them directly
        # in the 'application_href' string
        with open(self.api_key_file) as f:
            extract_from_yml = yaml.load(f.read())

        api_key_id = extract_from_yml['apiKey.id']
        api_key_secret = extract_from_yml['apiKey.secret']

        application_href = self.http_prefix + api_key_id + ':' + api_key_secret + self.app_href_without_http

        result = ClientApplicationBuilder(self.client_builder).\
                 set_application_href(application_href).\
                 build().\
                 application

        self.assertIsInstance(result, Application)

    def test_custom_properties_from_file(self):

        result = ClientApplicationBuilder().\
                 set_application_href(self.application_href).\
                 set_api_key_file_location(self.api_key_file).\
                 set_api_key_id_property_name('different.apiKey.id').\
                 set_api_key_secret_property_name('different.apiKey.secret').\
                 build().\
                 application

        self.assertIsInstance(result, Application)

    def test_custom_complex_properties_from_file(self):

        result = ClientApplicationBuilder().\
                 set_application_href(self.application_href).\
                 set_api_key_file_location(self.api_key_file).\
                 set_api_key_id_property_name('stormpath', 'apiKey', 'id').\
                 set_api_key_secret_property_name('stormpath', 'apiKey', 'secret').\
                 build().\
                 application

        self.assertIsInstance(result, Application)

    def test_no_application_href(self):
        with self.assertRaises(ValueError):
            ClientApplicationBuilder().build()

    def test_bad_client_builder(self):
        with self.assertRaises(TypeError):
            ClientApplicationBuilder('wrong')

    def test_bad_application_href(self):
        with self.assertRaises(ValueError):
            ClientApplicationBuilder().set_application_href('id:secret@stormpath.com/v1').build()



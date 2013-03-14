__author__ = 'ecrisostomo'

import urllib

import yaml

from stormpath.client import ClientBuilder
from stormpath.resource import Application
from stormpath.util import assert_instance, assert_true, assert_not_none


class ClientApplication:

    def __init__(self, client, application):
        self.client = client
        self.application = application

class ClientApplicationBuilder:

    def __init__(self, client_builder = None):

        self.application_href = None
        if (client_builder):
            assert_instance(client_builder, ClientBuilder, 'client_builder')
            self.client_builder = client_builder
        else:
            self.client_builder = ClientBuilder()

    def set_api_key_properties(self, properties):
        self.client_builder.set_api_key_properties(properties)
        return self

    def set_api_key_file_location(self, api_key_file_location):
        self.client_builder.set_api_key_file_location(api_key_file_location)
        return self

    def set_api_key_id_property_name(self, *api_key_id_property_name):
        self.client_builder.set_api_key_id_property_name(*api_key_id_property_name)
        return self

    def set_api_key_secret_property_name(self, *api_key_secret_property_name):
        self.client_builder.set_api_key_secret_property_name(*api_key_secret_property_name)
        return self

    def set_application_href(self, application_href):
        self.application_href = application_href
        return self

    def build(self):

        assert_not_none(self.application_href, "'application_href' property must be specified when using this builder implementation.")

        cleaned_href = self.application_href[0:len(self.application_href)] #just returning a copy

        at_sigh_index = cleaned_href.find('@')

        if at_sigh_index > 0: #otherwise an apiKey File/YAML/etc for the API Key is required

            parts = self._get_href_with_user_info_(cleaned_href, at_sigh_index)

            cleaned_href = parts[0] + parts[2]

            parts = parts[1].split(':', 1)

            api_key_properties = self._create_api_key_properties_(parts)

            self.set_api_key_properties(api_key_properties)

        assert_true(cleaned_href.find('http') == 0 and cleaned_href.find('://') > 0, 'Invalid application href URL')

        client = self._build_client_()

        application = client.data_store.get_resource(cleaned_href, Application)

        return ClientApplication(client, application)


    def _build_client_(self):
        return self.client_builder.build()

    def _get_href_with_user_info_(self, href, at_sign_index):
        assert_instance(href, str, 'href')
        assert_instance(at_sign_index, int, 'at_sign_index')

        double_slash_index = href.find('//')

        assert_true(double_slash_index > 0, 'Invalid application href URL')

        parts = {}
        parts[0] = href[0:double_slash_index + 2] #up to and including the double slash
        parts[1] = href[double_slash_index + 2:at_sign_index] #raw user info
        parts[2] = href[at_sign_index + 1:len(href)] #after the @ character

        return parts

    def _create_api_key_properties_(self, pair):
        assert_true(len(pair) == 2, 'application_href userInfo segment must consist' +
                                    ' of the following format: apiKeyId:apiKeySecret')

        properties = {'apiKey.id' : urllib.parse.unquote(pair[0]), 'apiKey.secret' : urllib.parse.unquote(pair[1])}

        return yaml.dump(properties)





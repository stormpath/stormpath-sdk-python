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
    """
    A "Builder design pattern":http://en.wikipedia.org/wiki/Builder_pattern implementation similar to
    the *ClientBuilder*, but focused on single-application interaction with Stormpath.

    Description

        The *ClientBuilder* produces a *Client* instance useful for interacting with any aspect
        of an entire Stormpath Tenant's data space.  However, a software application may only be interested in its own
        functionality and not the entire Stormpath Tenant data space.

        The *ClientApplicationBuilder* provides a means to more easily acquiring a single
        *Application* instance.  From this *Application* instance, everything a particular
        Application needs to perform can be based off of this instance and the wider-scoped concerns of an entire Tenant can be ignored.

    Default Usage

        this can be a file disk or url location as well:
        location = "/home/jsmith/.stormpath/apiKey.yml"

        app_href = "https://api.stormpath.com/v1/applications/YOUR_APP_UID_HERE"

        application = ClientApplicationBuilder().\
                      set_api_key_file_location(location).\
                      *set_application_href(app_href)*.\
                      build().\
                      application

    After acquiring the *Application* instance, you can interact with it to login accounts, reset passwords,
    etc.

    Service Provider Usage with only an Application URL

        Some hosting service providers (e.g. like "Heroku":http://www.heroku.com) do not allow easy access to
        a configuration file and therefore it might be difficult to reference an API Key File.  If you cannot reference an
        API Key File via the *YAML file* or *YAML string object* or *url*
        via *ClientBuilder().set_api_key_file_location(str)*, the Application HREF URL must contain the
        API Key embedded as the *"user info"http://en.wikipedia.org/wiki/URI_scheme* portion of the
        URL.  For example:

            https://apiKeyId:apiKeySecret@api.stormpath.com/v1/applications/YOUR_APP_UID_HERE

        Notice this is just a normal Application HREF url with the *apiKeyId:apiKeySecret@* part added in.

        Example usage:

            appHref = "https://apiKeyId:apiKeySecret@api.stormpath.com/v1/applications/YOUR_APP_UID_HERE"

            application = ClientApplicationBuilder().\
                          set_application_href(appHref).\
                          build().\
                          application

    *WARNING: ONLY use the embedded API Key technique if you do not have access to YAML file or
    YAML string object or url via ClientApplicationBuilder().set_api_key_file_location(str)*.
    File based API Key storage is a more secure technique than embedding the key in the URL itself.  Also, again,
    NEVER share your API Key Secret with *anyone* (not even co-workers).
    Stormpath staff will never ask for your API Key Secret.

    :see set_api_key_file_location(str)
    :see #set_application_href(str)
    """

    def __init__(self, client_builder = None):

        self.application_href = None
        if (client_builder):
            assert_instance(client_builder, ClientBuilder, 'client_builder')
            self.client_builder = client_builder
        else:
            self.client_builder = ClientBuilder()

    def set_api_key_properties(self, properties):
        """
        Allows usage of a YAML loadable string object
        instead of loading a YAML file via *set_api_key_file_location(apiKeyFileLocation)* configuration.

        The YAML contents and property name overrides function the same as described in the
        *set_api_key_file_location(setApiKeyFileLocation)* docstring.

        :param properties: the YAML string object to use to load the API Key ID and Secret.
        :returns this ClientApplicationBuilder instance for method chaining.
        """
        self.client_builder.set_api_key_properties(properties)
        return self

    def set_api_key_file_location(self, api_key_file_location):
        """
        Sets the location of the YAML file to load containing the API Key (Id and secret) used by the
        Client to communicate with the Stormpath REST API.

        You may load files from the filesystem, or URLs just specifying the file location.

        File Contents

            When the file is loaded, the following name/value pairs are expected to be present by default:


                    Key                 Value

                    apiKey.id           An individual account's API Key ID
                    apiKey.secret       The API Key Secret (password) that verifies the paired API Key ID.</td>


        Assuming you were using these default property names, your *ClientApplicationBuilder* usage might look like the
        following:

            location = "/home/jsmith/.stormpath/apiKey.yml";

            application_href = 'https://api.stormpath.com/v1/applications/YOUR_APP_UID_HERE'

            application = ClientApplicationBuilder().\
                          set_application_href(appHref).\
                          set_api_key_file_location(location).\
                          build().\
                          application

        Custom Property Names

            If you want to control the property names used in the file, you may configure them via
            *set_api_key_id_property_name(api_key_id_property_name)* and
            *set_api_key_secret_property_name(api_key_secret_property_name)*.

            For example, if you had a */home/jsmith/.stormpath/apiKey.yml* file with the following
            name/value pairs:

                myStormpathApiKeyId = 'foo'
                myStormpathApiKeySecret = 'mySuperSecretValue'

            Your *ClientApplicationBuilder* usage would look like the following:

                location = "/home/jsmith/.stormpath/apiKey.yml"

                application = ClientApplicationBuilder().\
                              set_application_href(application_href).\
                              set_api_key_file_location(location).\
                              set_api_key_id_property_name(myStormpathApiKeyId).\
                              set_api_key_secret_property_name(myStormpathApiKeySecret).\
                              build().\
                              application

        :param location: the file or url location of the API Key *.yml* file to load when
                        constructing the API Key to use for communicating with the Stormpath REST API.

        :returns the ClientApplicationBuilder instance for method chaining.
        """
        self.client_builder.set_api_key_file_location(api_key_file_location)
        return self

    def set_api_key_id_property_name(self, *api_key_id_property_name):
        """
        Sets the name used to query for the API Key ID from a YAML string instance.

        The *api_key_id_property_name* key can be as deep as needed, as long as it comes
        in the exact path order.

        Example: Having the file 'apiKey.yml' with the following content:

                  stormpath:
                    apiKey:
                    id: myStormpathApiKeyId

        The method should be called as follows:

                  ClientApplicationBuilder().set_api_key_id_property_name('stormpath', 'apiKey', 'id')

        :param api_key_id_property_name: the name used to query for the API Key ID from a YAML string/file.
        :returns the ClientApplicationBuilder instance for method chaining.
        """
        self.client_builder.set_api_key_id_property_name(*api_key_id_property_name)
        return self

    def set_api_key_secret_property_name(self, *api_key_secret_property_name):
        """
        Sets the name used to query for the API Key Secret from a YAML string instance.

        The *api_key_secret_property_name* key can be as deep as needed, as long as it comes
        in the exact path order.

        Example: Having the file 'apiKey.yml' with the following content:

                  stormpath:
                    apiKey:
                    secret: myStormpathApiKeySecret

        The method should be called as follows:

                  ClientApplicationBuilder().set_api_key_secret_property_name('stormpath', 'apiKey', 'secret')

        :param api_key_secret_property_name: the name used to query for the API Key Secret from a YAML string/file.
        :returns the ClientApplicationBuilder instance for method chaining.
        """
        self.client_builder.set_api_key_secret_property_name(*api_key_secret_property_name)
        return self

    def set_application_href(self, application_href):
        """
        Sets the fully qualified Stormpath Application HREF (a URL) to use to acquire the Application instance when
        *build()* is called.  See the Class-level docstring for usage scenarios.

        :param application_href: the fully qualified Stormpath Application HREF (a URL) to use to acquire the
                               Application instance when *build()* is called.
        :returns this ClientApplicationBuilder instance for method chaining.
        """
        self.application_href = application_href
        return self

    def build(self):
        """
        Builds a Client and Application wrapper instance based on the configured
        *set_application_href*. See the Class-level docstring for usage scenarios.

        :returns a Client and Application wrapper instance based on the configured *set_application_href*.
        """

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





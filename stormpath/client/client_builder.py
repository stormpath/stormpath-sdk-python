__author__ = 'ecrisostomo'

import yaml
from stormpath.client import ApiKey, Client
from stormpath.http import HttpClientRequestExecutor, Request
from stormpath.util import NestedValueNotFoundError, search_in_dict

class ClientBuilder:
    """
     A "Builder design pattern":http://en.wikipedia.org/wiki/Builder_pattern implementation used to
     construct {@link Client} instances.

     The *ClientBuilder* is especially useful for constructing Client instances with Stormpath API Key
     information loaded from an external *.yml* file (or YAML-valid string) to ensure the API Key secret
     (password) does not reside in plaintext in code.

     Example usage:

        location = "/home/jsmith/.stormpath/apiKey.yml";

        client = ClientBuilder().set_api_key_file_location(location).build()

     You may load files from the filesystem or URLs by specifying the file location.
     See set_api_key_file_location(location) for more information.
    """

    def __init__(self):
        self.api_key_id_property_name = "apiKey.id"
        self.api_key_secret_property_name = "apiKey.secret"
        self.api_key_properties, self.api_key_file_location, self.base_url = None, None, None

    def set_api_key_properties(self, properties):
        """
        Allows usage of a YAML loadable string instead of loading a YAML file via
        set_api_key_file_location(location) configuration.

        The YAML contents and property name overrides function the same as described in the
        set_api_key_file_location(location) docstring.

        :param properties: the YAML string to use to load the API Key ID and Secret.
        :returns the ClientBuilder instance for method chaining.
        """
        self.api_key_properties = properties
        return self

    def set_api_key_file_location(self, location):
        """
        Sets the location of the YAML file to load containing the API Key (Id and secret) used by the
        Client to communicate with the Stormpath REST API.

        You may load files from the filesystem, or URLs just specifying the file location.

        File Contents

            When the file is loaded, the following name/value pairs are expected to be present by default:


                    Key                 Value

                    apiKey.id           An individual account's API Key ID
                    apiKey.secret       The API Key Secret (password) that verifies the paired API Key ID.</td>


        Assuming you were using these default property names, your *ClientBuilder* usage might look like the
        following:

            location = "/home/jsmith/.stormpath/apiKey.yml";

            client = ClientBuilder().set_api_key_file_location(location).build()

        Custom Property Names

            If you want to control the property names used in the file, you may configure them via
            *set_api_key_id_property_name(api_key_id_property_name)* and
            *set_api_key_secret_property_name(api_key_secret_property_name)*.

            For example, if you had a */home/jsmith/.stormpath/apiKey.yml* file with the following
            name/value pairs:

                myStormpathApiKeyId = 'foo'
                myStormpathApiKeySecret = 'mySuperSecretValue'

            Your *ClientBuilder* usage would look like the following:

                location = "/home/jsmith/.stormpath/apiKey.yml"

            client = ClientBuilder().\
                     set_api_key_file_location(location).\
                     set_api_key_id_property_name("myStormpathApiKeyId").\
                     set_api_key_secret_property_name("myStormpathApiKeySecret").\
                     build()

        :param location: the file or url location of the API Key *.yml* file to load when
                        constructing the API Key to use for communicating with the Stormpath REST API.

        :returns the ClientBuilder instance for method chaining.
        """
        self.api_key_file_location = location
        return self

    def set_api_key_id_property_name(self, *api_key_id_property_name):
        """
        Sets the name used to query for the API Key ID from a YAML instance.

        The *api_key_id_property_name* key can be as deep as needed, as long as it comes
        in the exact path order.

        Example: Having the file 'apiKey.yml' with the following content:

                  stormpath:
                    apiKey:
                    id: myStormpathApiKeyId

        The method should be called as follows:

                  ClientBuilder().set_api_key_id_property_name('stormpath', 'apiKey', 'id')

        :param api_key_id_property_name: the name used to query for the API Key ID from a YAML string/file.
        :returns the ClientBuilder instance for method chaining.
        """
        self.api_key_id_property_name = api_key_id_property_name
        return self

    def set_api_key_secret_property_name(self, *api_key_secret_property_name):
        """
        Sets the name used to query for the API Key Secret from a YAML instance.

        The *api_key_secret_property_name* key can be as deep as needed, as long as it comes
        in the exact path order.

        Example: Having the file 'apiKey.yml' with the following content:

                  stormpath:
                    apiKey:
                    secret: myStormpathApiKeySecret

        The method should be called as follows:

                  ClientBuilder().set_api_key_secret_property_name('stormpath', 'apiKey', 'secret')

        :param api_key_secret_property_name: the name used to query for the API Key Secret from a YAML string/file.
        :returns the ClientBuilder instance for method chaining.
        """
        self.api_key_secret_property_name = api_key_secret_property_name
        return self

    def set_base_url(self, base_url):
        self.base_url = base_url
        return self

    def build(self):
        """
        Constructs a new *Client* instance based on the ClientBuilder's current configuration state.

        :returns a new *Client* instance based on the ClientBuilder's current configuration state.
        """

        if self.api_key_properties:
            extract_from_yml = yaml.load(self.api_key_properties)

        else:

            # need to load the properties file
            file_content = self._get_available_file_content_()

            if not file_content:
                raise ValueError('No API Key file could be found or loaded from a file location. ' +
                'Please  configure the "apiKeyFileLocation" property or alternatively configure a ' +
                'YAML compliant string.')

            extract_from_yml = yaml.load(file_content)

        api_key_id = self._get_required_property_value_(extract_from_yml, 'apiKeyId', self.api_key_id_property_name)
        api_key_secret = self._get_required_property_value_(extract_from_yml, 'apiKeySecret', self.api_key_secret_property_name)

        api_key = ApiKey(api_key_id, api_key_secret)

        return Client(api_key, self.base_url)

    def _get_available_file_content_(self):
        if 'http' in self.api_key_file_location:
            request = Request(http_method='get', href=self.api_key_file_location)
            executor = HttpClientRequestExecutor()

            try:

                response = executor.execute_request(request)

                if not response.is_error():
                    return response.body

            except:
                return None

        else:

            with open(self.api_key_file_location) as f:
                return f.read()


    def _get_required_property_value_(self, dict_from_yml, master_name, property_name):

        try:

            property_name = property_name if (isinstance(property_name, tuple)) else [property_name]
            return search_in_dict(dict_from_yml, property_name)

        except NestedValueNotFoundError:

            raise ValueError("There is no '" + ":".join(str(prop_name) for prop_name in property_name) + "' property in the " +
                             "configured apiKey YAML.  You can either specify that property or " +
                             "configure the {}_property_name value on the ClientBuilder to specify a ".format(master_name) +
                             "custom property name.")




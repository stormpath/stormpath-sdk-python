#
# Copyright 2012, 2013 Stormpath, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


import jprops
from stormpath.api_key import ApiKey
from stormpath.util import assert_not_none
from stormpath.resource.tenant import Tenant
from stormpath.http.http_client_request_executor import HttpClientRequestExecutor
from stormpath.data_store import DataStore


class Client(object):
    """
    The main class for access to different portions of Stormpath.

    Usage
        To create a client object, two properties are required:
            The secret key
            The key id

        Regarding those properties, the constructor for the Client object accepts
        three different types of arguments:

            A dictionary containing the secret key and the id
            client = Client(api_key={'id': id, 'secret': secret})

            An instance of the ApiKey class
            api_key = ApiKey(id, secret)
            client = Client(api_key=api_key)

            The location of a Java properties file containing the key and id
            file_location = "./apiKey.properties"
            client = Client(api_key_file_location=file_location)

        Just like the Tenant, it can be used access applications, directories etc.
        of the authenticated user.
    """

    def __init__(self, api_key_file_location=None, api_key=None, base_url=None,
            api_key_id_property_name=None, api_key_secret_property_name=None):

        if isinstance(api_key, dict):
            self.api_key = ApiKey(api_key.get('id'), api_key.get('secret'))
        elif isinstance(api_key, ApiKey):
            self.api_key = api_key
        else:
            self.api_key = self.load_api_key_file(api_key_file_location,
                api_key_id_property_name, api_key_secret_property_name)

        assert_not_none(self.api_key, "No API key has been provided. " +
            "Please pass an 'api_key' or 'api_key_file_location' " +
            "to the Client constructor.")

        request_executor = HttpClientRequestExecutor(self.api_key)
        self.data_store = DataStore(request_executor, self, base_url)

    @property
    def tenant(self):
        return Tenant("/tenants/current", self)

    @property
    def client(self):
        return self

    @property
    def applications(self):
        return self.tenant.applications

    @property
    def directories(self):
        return self.tenant.directories

    @property
    def accounts(self):
        return self.tenant.accounts

    def load_api_key_file(self, api_key_file_location=None,
            id_property_name=None, secret_property_name=None):
        try:
            with open(api_key_file_location) as fp:
                api_key_properties = jprops.load_properties(fp)
        except:
            raise ValueError("No API Key file could be found " +
                "or loaded from api_key_file_location.")

        id_property_name = id_property_name or 'apiKey.id'
        secret_property_name = secret_property_name or 'apiKey.secret'

        api_key_id = api_key_properties.get(id_property_name, None)
        assert_not_none(api_key_id, "No API id in properties. " +
            "Please provide a 'apiKey.id' property in '" +
            api_key_file_location +
            "' or pass in an 'api_key_id_property_name' to the Client " +
            "constructor to specify an alternative property.")

        api_key_secret = api_key_properties.get(secret_property_name, None)
        assert_not_none(api_key_secret, "No API id in properties. " +
            "Please provide a 'apiKey.id' property in '" +
            api_key_file_location +
            "' or pass in an 'api_key_id_property_name' to the Client " +
            "constructor to specify an alternative property.")

        return ApiKey(api_key_id, api_key_secret)

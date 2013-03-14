__author__ = 'ecrisostomo'

from stormpath.util import assert_instance
from stormpath.ds import DataStore
from stormpath.http import HttpClientRequestExecutor
from stormpath.resource import Tenant

class Client:

    def __init__(self, api_key, base_url = None):
        assert_instance(api_key, ApiKey, 'api_key')
        request_executor = HttpClientRequestExecutor(api_key)
        self.data_store = DataStore(request_executor, base_url)

    @property
    def current_tenant(self):
        return self.data_store.get_resource('/tenants/current', Tenant)

class ApiKey:

    def __init__(self, id, secret):
        self.id = id
        self.secret = secret
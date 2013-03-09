__author__ = 'ecrisostomo'

from test.test_base import BaseTest
from stormpath.client.client import Client
from stormpath.ds.data_store import DataStore

class ClientTest(BaseTest):

    def test_create_client(self):
        self.assertIsInstance(self.client, Client)
        self.assertIsInstance(self.client.data_store, DataStore)

    def test_create_client_fail(self):
        with self.assertRaises(TypeError):
            Client(api_key=None, base_url='nevermind')

    def test_current_tenant(self):
        tenant = self.client.current_tenant
        self.assertEqual(tenant.name, 'System Tenant')
        self.assertEqual(tenant.key, 'system')

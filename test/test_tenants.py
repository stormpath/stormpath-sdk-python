__author__ = 'ecrisostomo'

from unittest import TestCase

from stormpath.client.client import Client, ApiKey


class TenantsTest(TestCase):

    def setUp(self):
        id, secret = 'id', 'secret'
        self.client = Client(api_key=ApiKey(id=id, secret=secret), base_url='http://localhost:8080/v1')

    def test_current_tenant(self):
        tenant = self.client.current_tenant
        self.assertEqual(tenant.name, 'System Tenant')
        self.assertEqual(tenant.key, 'system')

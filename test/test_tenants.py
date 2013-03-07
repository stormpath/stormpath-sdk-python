__author__ = 'ecrisostomo'

from test import BaseTest

class TenantsTest(BaseTest):

    def test_current_tenant(self):
        tenant = self.client.current_tenant
        self.assertEqual(tenant.name, 'System Tenant')
        self.assertEqual(tenant.key, 'system')

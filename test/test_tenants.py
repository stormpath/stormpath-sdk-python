__author__ = 'ecrisostomo'

from test.test_base import BaseTest
from stormpath.resource.applications import Application
from stormpath.resource.resource_error import ResourceError

class TenantsTest(BaseTest):


    def test_properties(self):
        tenant = self.client.current_tenant
        self.assertTrue(tenant.name)
        self.assertTrue(tenant.key)

    def test_create_application_fail(self):
        tenant = self.client.current_tenant
        with self.assertRaises(TypeError):
            tenant.create_application(None)

    def test_create_application(self):
        tenant = self.client.current_tenant
        app_name = "New Python SDK App"
        application = self.client.data_store.instantiate(Application)
        application.name = app_name
        tenant.create_application(application=application)

        self.created_applications.append(application)

        self.assertTrue(application.properties['href'])
        self.assertIsInstance(application, Application)
        self.assertEqual(application.name, app_name)

    def test_verify_account_email_fail(self):
        tenant = self.client.current_tenant
        with self.assertRaises(ResourceError):
            tenant.verify_account_email('badtoken')

    def test_verify_account_email(self):
        pass # TODO: implement, ideally using command line args for the token


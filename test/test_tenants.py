__author__ = 'ecrisostomo'

from test.test_base import BaseTest
from stormpath.resource import Account, Application, ApplicationList, Directory, DirectoryList, ResourceError

class TenantsTest(BaseTest):


    def test_properties(self):
        tenant = self.client.current_tenant

        application1 = self.client.data_store.instantiate(Application, {"name" : "Tenant's App 1"})
        application2 = self.client.data_store.instantiate(Application, {"name" : "Tenant's App 2"})
        tenant.create_application(application=application1)
        tenant.create_application(application=application2)

        self.created_applications.append(application1)
        self.created_applications.append(application2)

        directory1 = self.client.data_store.instantiate(Directory, {"name" : "Tenant's Dir 1"})
        directory2 = self.client.data_store.instantiate(Directory, {"name" : "Tenant's Dir 2"})
        self.client.data_store.create('directories', directory1, Directory)
        self.client.data_store.create('directories', directory2, Directory)

        self.created_directories.append(directory1)
        self.created_directories.append(directory2)

        applications = tenant.applications
        directories = tenant.directories
        self.assertIsInstance(applications, ApplicationList)
        self.assertIsInstance(directories, DirectoryList)

        new_apps = 0
        for app in applications:
            self.assertIsInstance(app, Application)
            if app.name == application1.name or app.name == application2.name:
                new_apps += 1

        new_dirs = 0
        for dir in directories:
            self.assertIsInstance(dir, Directory)
            if dir.name == directory1.name or dir.name == directory2.name:
                new_dirs += 1

        self.assertEquals(new_apps, 2)
        self.assertEquals(new_dirs, 2)
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

        #TODO: change this test because it fails after the 1st time it succeeds
        account = self.client.current_tenant.verify_account_email('4lWcj3aj6iZ0jeQDCVQ6nz')

        self.assertIsInstance(account, Account)
        self.assertTrue(account.href)
        self.assertTrue(account.given_name)


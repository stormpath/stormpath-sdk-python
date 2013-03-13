__author__ = 'ecrisostomo'

from test.test_base import BaseTest

from stormpath.auth import AuthenticationResult, UsernamePasswordRequest
from stormpath.resource import Account, AccountList, Application, ResourceError, Tenant, enabled, disabled

class ApplicationsTest(BaseTest):

    def test_properties(self):

        app_name, app_desc = "New App Name", "New App Desc"
        application = self._create_application_(app_name, app_desc)

        self.assertEqual(application.name, app_name)
        self.assertEqual(application.description, app_desc)
        self.assertIsInstance(application.status, enabled.__class__)
        self.assertIsInstance(application.accounts, AccountList)
        self.assertIsInstance(application.tenant, Tenant)

    def test_update_attributes(self):
        app_name, app_desc = "New App Name", "New App Desc"
        application = self._create_application_(app_name, app_desc)

        app_name, app_desc, status = "Updated App Name", "Updated App Desc", disabled
        application.name = app_name
        application.description = app_desc
        application.status = status
        application.save()

        self.assertEqual(application.name, app_name)
        self.assertEqual(application.description, app_desc)
        self.assertEqual(application.status, status)
        self.assertIsInstance(application.status, disabled.__class__)


    def test_authenticate_account(self):

        href = 'applications/ys-NzadoQaelH2rDF03VuQ'
        application = self.client.data_store.get_resource(href, Application)

        result = application.authenticate_account(UsernamePasswordRequest('pythonsdk', 'superP4ss'))

        self.assertIsInstance(result, AuthenticationResult)

        self.assertIsInstance(result.account, Account)

    def test_authenticate_account_fail(self):

        href = 'applications/ys-NzadoQaelH2rDF03VuQ'
        application = self.client.data_store.get_resource(href, Application)

        try:

            application.authenticate_account(UsernamePasswordRequest('pythonsdk', 'bad'))
            self.assertTrue(False)

        except ResourceError as re:
            self.assertTrue(re.code == 400 and 'username or password' in re.message
            and 'support@stormpath.com' in re.more_info and re.status == 400
            and 'username or password' in re.developer_message)

    def test_send_password_reset_email(self):
        href = 'applications/ys-NzadoQaelH2rDF03VuQ'
        application = self.client.data_store.get_resource(href, Application)

        email = 'fakeuseragain@mailinator.com'
        account = application.send_password_reset_email(email)

        self.assertIsInstance(account, Account)
        self.assertTrue(account.href)
        self.assertEquals(account.email, email)

    def test_verify_password_reset_token(self):

        href = 'applications/ys-NzadoQaelH2rDF03VuQ'
        application = self.client.data_store.get_resource(href, Application)

        token = '5YvR5x01v2jRp1OE56Nbvf'

        account = application.verify_password_reset_token(token)

        self.assertIsInstance(account, Account)
        self.assertTrue(account.href)
        self.assertTrue(account.given_name)

    def _create_application_(self, name, description = None, status = enabled):
        tenant = self.client.current_tenant

        application = self.client.data_store.instantiate(Application)
        application.name = name
        application.description = description
        application.status = status

        tenant.create_application(application)

        self.created_applications.append(application)
        return application


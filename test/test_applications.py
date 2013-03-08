__author__ = 'ecrisostomo'

from test import BaseTest

from stormpath.auth.request_result import AuthenticationResult, UsernamePasswordRequest
from stormpath.resource.accounts import Account
from stormpath.resource.resource_error import ResourceError
from stormpath.resource.applications import Application

class ApplicationsTest(BaseTest):

    def test_authenticate_account(self):

        href = 'applications/ys-NzadoQaelH2rDF03VuQ'
        application = self.client.data_store.get_resource(href, Application)

        result = application.authenticate_account(UsernamePasswordRequest('pythonsdk', 'superP4ss'))

        self.assertIsInstance(result, AuthenticationResult)

        self.assertIsInstance(result.account, Account)

    def test_fail_authenticate_account(self):

        href = 'applications/ys-NzadoQaelH2rDF03VuQ'
        application = self.client.data_store.get_resource(href, Application)

        try:

            application.authenticate_account(UsernamePasswordRequest('pythonsdk', 'bad'))
            self.assertTrue(False)

        except ResourceError as re:
            self.assertTrue(re.code == 400 and 'username or password' in re.message
            and 'support@stormpath.com' in re.more_info and re.status == 400
            and 'username or password' in re.developer_message)
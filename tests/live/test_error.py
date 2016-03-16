"""Live tests of common error functionality.

We can use (almost) any resource here - Account is a convenient choice.
"""

from .base import AuthenticatedLiveBase
from stormpath.resources import Account
from stormpath.error import Error


class TestError(AuthenticatedLiveBase):

    def test_error_raised_with_error_json(self):
        error = None

        try:
            acc = Account(
                self.client, '%s/i.do.not.exist' % self.client.BASE_URL)
            acc.given_name
        except Error as e:
            error = e

        self.assertIsNotNone(error)
        self.assertIsInstance(error, Error)
        msg = str(error)
        self.assertEqual(error.status, 404)
        self.assertEqual(error.code, 404)
        self.assertEqual(error.developer_message, msg)
        self.assertEqual(error.user_message, msg)
        self.assertTrue(error.more_info)
        self.assertEqual(error.message, msg)

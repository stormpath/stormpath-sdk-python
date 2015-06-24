""""
Integration tests for various pieces involved in external provider support.
"""

from unittest import TestCase, main
from stormpath.resources import AccountCreationPolicy

try:
    from mock import MagicMock
except ImportError:
    from unittest.mock import MagicMock


class TestAccountCreationPolicy(TestCase):

    def test_modifying_account_creation_policy(self):
        ds = MagicMock()
        ds.update_resource.return_value = {}

        pp = AccountCreationPolicy(
            client=MagicMock(data_store=ds, BASE_URL='http://example.com'),
            href='account-creation-policy')

        pp._set_properties(
            {
                'verification_email_status':
                    AccountCreationPolicy.EMAIL_STATUS_ENABLED
            })
        pp.save()

        ds.update_resource.assert_called_once_with(
            'account-creation-policy',
            {
                'verificationEmailStatus':
                    AccountCreationPolicy.EMAIL_STATUS_ENABLED
            })


if __name__ == '__main__':
    main()

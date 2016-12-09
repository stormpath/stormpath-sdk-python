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

    def setUp(self):
        self.ds = MagicMock()
        self.ds.update_resource.return_value = {}

        self.pp = AccountCreationPolicy(
                    client=MagicMock(data_store=self.ds,
                                     BASE_URL='http://example.com'),
                    href='account-creation-policy'
        )

    def test_modifying_account_creation_policy(self):
        self.pp._set_properties(
            {
                'verification_email_status':
                    AccountCreationPolicy.EMAIL_STATUS_ENABLED
            })
        self.pp.save()

        self.ds.update_resource.assert_called_once_with(
            'account-creation-policy',
            {
                'verificationEmailStatus':
                    AccountCreationPolicy.EMAIL_STATUS_ENABLED
            })

    def test_modifying_email_domain_whitelist_and_blacklist(self):
        self.pp._set_properties(
            {
                'email_domain_whitelist':
                    ['gmail.com', 'yahoo.com', 'stormpath.com'],
                'email_domain_blacklist':
                    ['mail.ru', 'somedomain.com']
            }
        )
        self.pp.save()

        self.ds.update_resource.assert_called_once_with(
            'account-creation-policy',
            {
                'emailDomainWhitelist':
                    ['gmail.com', 'yahoo.com', 'stormpath.com'],
                'emailDomainBlacklist':
                    ['mail.ru', 'somedomain.com']
            }
        )

if __name__ == '__main__':
    main()

""""
Integration tests for various pieces involved in external provider support.
"""

from unittest import TestCase, main
from stormpath.resources import AccountLinkingPolicy

try:
    from mock import MagicMock
except ImportError:
    from unittest.mock import MagicMock


class TestAccountLinkingPolicy(TestCase):

    def test_modifying_account_linking_policy(self):
        ds = MagicMock()
        ds.update_resource.return_value = {}

        pp = AccountLinkingPolicy(
            client=MagicMock(data_store=ds, BASE_URL='http://example.com'),
            href='account-linking-policy')

        pp._set_properties(
            {
                'status':
                    AccountLinkingPolicy.STATUS_ENABLED,
                'automatic_provisioning':
                    AccountLinkingPolicy.AUTOMATIC_PROVISIONING_ENABLED,
                'matching_property':
                    AccountLinkingPolicy.MATCHING_PROPERTY_EMAIL
            })
        pp.save()

        ds.update_resource.assert_called_once_with(
            'account-linking-policy',
            {
                'status':
                    AccountLinkingPolicy.STATUS_ENABLED,
                'automaticProvisioning':
                    AccountLinkingPolicy.AUTOMATIC_PROVISIONING_ENABLED,
                'matchingProperty':
                    AccountLinkingPolicy.MATCHING_PROPERTY_EMAIL
            })


if __name__ == '__main__':
    main()

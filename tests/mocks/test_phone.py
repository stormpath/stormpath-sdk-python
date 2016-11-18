from unittest import TestCase
from stormpath.resources.phone import Phone

try:
    from mock import MagicMock
except ImportError:
    from unittest.mock import MagicMock


class TestPhone(TestCase):

    def setUp(self):

        self.client = MagicMock(BASE_URL='http://example.com')
        self.phone = Phone(
            self.client,
            properties={
                'number': '+123456789',
                'verification_status': 'UNVERIFIED'})

    def test_is_verified(self):
        # Ensure that verified status method is properly working.

        self.assertFalse(self.phone.is_verified())
        self.phone.verification_status = 'VERIFIED'
        self.assertTrue(self.phone.is_verified())

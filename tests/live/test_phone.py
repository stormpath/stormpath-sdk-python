"""Live tests of Factors and MFA functionality."""

from .base import MFABase
from stormpath.error import Error as StormpathError


class TestPhone(MFABase):

    def test_verified_phone_number_immutable(self):
        # Ensure that a number from a verified Phone instance cannot be
        # changed.

        # Ensure that an unverified phone can change its number.
        self.phone.number = '+15005559999'
        self.assertEqual(self.phone.verification_status, 'UNVERIFIED')
        self.phone.save()

        # Ensure that a verified phone number is immutable.
        self.phone.verification_status = 'VERIFIED'
        self.phone.number = '+15005558888'

        with self.assertRaises(StormpathError) as error:
            self.phone.save()
        self.assertEqual(
            error.exception.message,
            'Verified phone numbers cannot be modified.')

    def test_phone_number_unique_on_account(self):
        # Ensure that phone numbers in an Account instance are unique.

        with self.assertRaises(StormpathError) as error:
            self.account.phones.create({'number': '+15005550006'})
        self.assertEqual(
            error.exception.message,
            'An existing phone with that number already exists' +
            ' for this Account.')

    def test_phone_numbers_not_unique_between_accounts(self):
        # Ensure that same phone numbers can exist between multiple accounts
        # in the same directory.

        new_username, new_account = self.create_account(self.app.accounts)

        # The number used here is the same as in self.phone.
        phone = new_account.phones.create({'number': '+15005550006'})
        self.assertEqual(self.phone.number, phone.number)
        self.assertEqual(
            self.phone.account.directory.href, phone.account.directory.href)

    def test_phone_factor_deleted(self):
        # Ensure that all factors that reference a phone instance are deleted
        # when that phone instance is deleted.

        factor = self.account.factors.create({
            "phone": self.phone,
            "type": "SMS"},
            challenge=False)
        self.phone.delete()

        with self.assertRaises(StormpathError) as error:
            factor.refresh()
        self.assertEqual(
            error.exception.message, 'The requested resource does not exist.')

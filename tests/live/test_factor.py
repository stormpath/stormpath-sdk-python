"""Live tests of Factors and MFA functionality."""

from .base import AccountBase
from stormpath.resources.factor import FactorList
from stormpath.resources.challenge import Challenge, ChallengeList
from stormpath.resources.phone import PhoneList
from stormpath.error import Error


class TestFactor(AccountBase):

    def setUp(self):
        super(TestFactor, self).setUp()
        self.username, self.account = self.create_account(self.app.accounts)

        # This is Twilio's official testing phone number:
        # https://www.twilio.com/docs/api/rest/test-credentials#test-sms-messages
        self.phone_number = '+15005550006'

    def test_create(self):
        # Create a factor.

        data = {
            'phone': {'number': self.phone_number},
            'challenge': {'message': '${code}'},
            'type': 'SMS'
        }
        factor = self.account.factors.create(properties=data)
        self.account.refresh()

        # Ensure that the factor and phone resources have been successfully
        # added to the account instance.
        self.assertTrue(isinstance(self.account.factors, FactorList))
        self.assertEqual(len(self.account.factors.items), 1)
        self.assertEqual(self.account.factors.items[0].href, factor.href)
        self.assertTrue(isinstance(self.account.phones, PhoneList))
        self.assertTrue(len(self.account.phones.items), 1)
        self.assertEqual(
            self.account.phones.items[0].number, data['phone']['number'])

    def test_create_invalid_number(self):
        # Try creating a factor using an invalid phone number.

        data = {
            'phone': {'number': '+666'},
            'challenge': {'message': '${code}'},
            'type': 'SMS'
        }

        with self.assertRaises(Error) as error:
            self.account.factors.create(properties=data)
        self.assertEqual(
            error.exception.message, 'The provided phone number is invalid.')

    def test_create_with_challenge(self):
        # Create factor with challenge.

        data = {
            'phone': {'number': self.phone_number},
            'challenge': {'message': '${code}'},
            'type': 'SMS'
        }
        factor = self.account.factors.create(properties=data)
        self.account.refresh()

        # Ensure that the challenge list resource has been successfully
        # created.
        self.assertTrue(isinstance(factor.challenges, ChallengeList))

        # Ensure that the newly created factor created a challenge.
        self.assertEqual(len(factor.challenges.items), 1)
        self.assertTrue(isinstance(factor.most_recent_challenge, Challenge))

    def test_create_without_challenge(self):
        # Create factor without challenge.

        data = {
            'phone': {'number': self.phone_number},
            'type': 'SMS'
        }
        factor = self.account.factors.create(properties=data, challenge=False)
        self.account.refresh()

        # Ensure that the challenge list resource has been successfully
        # created.
        self.assertTrue(isinstance(factor.challenges, ChallengeList))

        # Ensure that the newly created factor did not create a challenge.
        self.assertEqual(len(factor.challenges.items), 0)
        self.assertEqual(factor.most_recent_challenge, None)

        # Ensure that passing the challenge params while challenge == False
        # won't create a challenge.
        factor.delete()
        data = {
            'phone': {'number': self.phone_number},
            'challenge': {'message': '${code}'},
            'type': 'SMS'
        }
        factor = self.account.factors.create(properties=data, challenge=False)
        self.account.refresh()

        # Ensure that the newly created factor did not create a challenge.
        self.assertEqual(len(factor.challenges.items), 0)
        self.assertIsNone(factor.most_recent_challenge)

    def test_challenge(self):
        # Create a challenge by challenging our factor.

        data = {
            'phone': {'number': self.phone_number},
            'type': 'SMS'
        }
        factor = self.account.factors.create(properties=data, challenge=False)
        self.account.refresh()

        # Ensure that the factor will create a challenge.
        self.assertEqual(len(factor.challenges.items), 0)
        challenge = factor.challenge_factor('${code}')
        self.assertEqual(len(factor.challenges.items), 1)

        # Ensure that you can create a new challenge on top of the old one.
        challenge2 = factor.challenge_factor('${code}')
        self.assertEqual(len(factor.challenges.items), 2)
        self.assertNotEqual(challenge, challenge2)

    def test_challenge_factor_message(self):
        # Specifying a custom message on factor challenge.

        data = {
            'phone': {'number': self.phone_number},
            'type': 'SMS'
        }
        factor = self.account.factors.create(properties=data, challenge=False)
        self.account.refresh()

        # Ensure that you cannot specify a message without a '${code}'
        # placeholder.
        message = 'This message is missing a placeholder.'
        with self.assertRaises(Error) as error:
            factor.challenge_factor(message)
        self.assertEqual(
            error.exception.message,
            "The challenge message must include '${code}'.")
        factor.refresh()
        self.assertIsNone(factor.most_recent_challenge)

        # Ensure that you can customize your message.
        message = 'This is my custom message: ${code}.'
        factor.challenge_factor(message)
        self.assertEqual(factor.most_recent_challenge.message, message)

        # Ensure that the default message will be set.
        default_message = 'Your verification code is ${code}'
        factor.challenge_factor()
        self.assertEqual(factor.most_recent_challenge.message, default_message)

    def test_create_factor_message(self):
        # Specifying a custom message on factor create.

        data = {
            'phone': {'number': self.phone_number},
            'challenge': {'message': 'This message is missing a placeholder.'},
            'type': 'SMS'
        }

        # Ensure that you cannot specify a message without a '${code}'
        # placeholder.
        with self.assertRaises(Error) as error:
            self.account.factors.create(properties=data, challenge=True)
        self.assertEqual(
            error.exception.message,
            "The challenge message must include '${code}'.")

        # Ensure that you can customize your message.
        data['challenge']['message'] = 'This is my custom message: ${code}.'
        factor = self.account.factors.create(properties=data, challenge=True)
        self.assertEqual(
            factor.most_recent_challenge.message, data['challenge']['message'])

        factor.delete()
        data.pop('challenge')

        # Ensure that the default message will be set.
        default_message = 'Your verification code is ${code}'
        factor = self.account.factors.create(properties=data, challenge=True)
        self.assertEqual(factor.most_recent_challenge.message, default_message)

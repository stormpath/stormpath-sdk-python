"""Live tests of Factors and MFA functionality."""

from .base import MFABase
from stormpath.resources.factor import FactorList
from stormpath.resources.challenge import Challenge, ChallengeList
from stormpath.resources.phone import PhoneList
from stormpath.error import Error


class TestFactor(MFABase):

    def test_create(self):
        # Create a factor.

        data = {
            'phone': self.phone,
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
            'phone': self.phone,
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
            'phone': self.phone,
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

        # Ensure that passing the challenge params while challenge=False
        # won't create a challenge.
        factor.delete()
        data = {
            'phone': self.phone,
            'challenge': {'message': '${code}'},
            'type': 'SMS'
        }
        with self.assertRaises(ValueError) as error:
            factor = self.account.factors.create(
                properties=data, challenge=False)
        error_msg = (
            'If challenge is set to False, it must also be absent ' +
            'from properties.')
        self.assertEqual(error.exception.message, error_msg)

        # Ensure that the newly created factor did not create a challenge.
        self.assertEqual(len(factor.challenges.items), 0)
        self.assertIsNone(factor.most_recent_challenge)

    def test_challenge_list(self):
        # Ensure that challenges are present in our ChallengeList after we've
        # created them.

        data = {
            'phone': self.phone,
            'type': 'SMS'
        }

        # Ensure that challenge=False will not create a challenge
        factor = self.account.factors.create(properties=data, challenge=False)
        factor.refresh()
        self.assertEqual(len(factor.challenges.items), 0)

        # Ensure that the factor will create a challenge.
        challenge = factor.challenge_factor(message='${code}')
        factor.refresh()
        self.assertEqual(len(factor.challenges.items), 1)

        # Ensure that you can create a new challenge on top of the old one.
        challenge2 = factor.challenge_factor(message='New ${code}')
        factor.refresh()
        self.assertEqual(len(factor.challenges.items), 2)
        self.assertNotEqual(challenge, challenge2)

    def test_challenge_factor_message(self):
        # Specifying a custom message on factor challenge.

        data = {
            'phone': self.phone,
            'type': 'SMS'
        }
        factor = self.account.factors.create(properties=data, challenge=False)

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
        factor.challenge_factor(message=message)
        factor.refresh()
        self.assertEqual(factor.most_recent_challenge.message, message)

        # Ensure that the default message will be set.
        default_message = 'Your verification code is ${code}'
        factor.challenge_factor()
        factor.refresh()
        self.assertEqual(factor.most_recent_challenge.message, default_message)

    def test_create_factor_message(self):
        # Specifying a custom message on factor create.

        data = {
            'phone': self.phone,
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

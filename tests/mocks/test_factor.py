from unittest import TestCase
from stormpath.resources.factor import Factor, FactorList
from stormpath.resources.challenge import Challenge, ChallengeList
from stormpath.data_store import DataStore

try:
    from mock import MagicMock, patch
except ImportError:
    from unittest.mock import MagicMock, patch


class TestFactor(TestCase):
    def setUp(self):

        self.client = MagicMock(BASE_URL='http://example.com')
        self.client.data_store = DataStore(MagicMock())
        self.factor = Factor(
            self.client,
            properties={
                'href': '/factors/factor_id',
                'name': 'factor',
                'type': 'SMS',
                'challenges': ChallengeList(
                    self.client, properties={'href': '/challenges'}),
                'verification_status': 'UNVERIFIED'
            })
        self.factors = FactorList(client=self.client, href='test/factors')
        self.challenge = Challenge(
            self.client,
            properties={
                'href': '/challenges/challenge_id',
                'factor': self.factor
            })

    def test_create_challenge_invalid(self):
        # Ensure that a ValueError is raised if challenge is set in properties
        # but challenge param is set to False.

        properties = {
            'type': 'SMS',
            'phone': {'number': '+666'},
            'challenge': {'message': '${code}'}
        }

        with self.assertRaises(ValueError) as error:
            self.factors.create(properties=properties, challenge=False)
        error_msg = (
            'If challenge is set to False, it must also be absent ' +
            'from properties.')
        self.assertEqual(str(error.exception), error_msg)

        # Ensure that a properly set create parameters won't raise the
        # ValueError.
        properties.pop('challenge')
        self.factors.create(properties=properties, challenge=False)

    @patch('stormpath.resources.challenge.ChallengeList.create')
    def test_challenge_factor_correct_params(self, create):
        # Ensure that message is properly passed on challenge create.

        create.return_value = self.challenge

        self.factor._set_properties({'most_recent_challenge': self.challenge})
        self.factor.challenge_factor(message='This is your message ${code}.')

        create.assert_called_once_with(
            properties={'message': 'This is your message ${code}.'})

    @patch('stormpath.resources.challenge.ChallengeList.create')
    def test_challenge_factor_google_authenticator_code(self, create):
        # Ensure that the code parameter is present when challenging
        # a google-authenticator factor.

        create.return_value = self.challenge

        self.factor._set_properties({'most_recent_challenge': self.challenge})
        self.factor.type = 'google-authenticator'

        # Ensure that the missing code will raise an error.
        with self.assertRaises(ValueError) as error:
            self.factor.challenge_factor()
        self.assertEqual(
            str(error.exception), 'When challenging a ' +
            'google-authenticator factor, activation code must be provided.')

        # Ensure that the code will challenge the factor.
        challenge = self.factor.challenge_factor(code='123456')
        self.assertEqual(challenge, self.challenge)

        # Ensure that challenge_factor did not create a request when the code
        # was missing.
        create.assert_called_once_with(properties={'code': '123456'})

    @patch('stormpath.resources.challenge.ChallengeList.create')
    def test_challenge_factor_message_default(self, create):
        # Ensure that the default message is properly set when challenging
        # factor.

        create.return_value = self.challenge

        self.factor._set_properties({'most_recent_challenge': self.challenge})
        self.factor.challenge_factor()

        create.assert_called_once_with(properties={'message': None})

    @patch('stormpath.resources.challenge.ChallengeList.create')
    def test_challenge_factor_message_custom(self, create):
        # Ensure that the default message is properly overridden when
        # challenging factor.

        create.return_value = self.challenge

        self.factor._set_properties({'most_recent_challenge': self.challenge})
        self.factor.challenge_factor(message='This is your message ${code}.')

        create.assert_called_once_with(
            properties={'message': 'This is your message ${code}.'})

    @patch('stormpath.resources.base.CollectionResource.create')
    def test_create_factor_message_custom(self, create):
        # Ensure that the custom message is properly set when creating a
        # factor with challenge=True.

        create.return_value = self.challenge

        properties = {
            'type': 'SMS',
            'phone': {'number': '+666'},
            'challenge': {'message': 'This is my custom message ${code}.'}
        }

        self.factors.create(properties=properties, challenge=True)
        create.assert_called_once_with(
            properties, challenge=True, expand=None)

    def test_is_verified(self):
        # Ensure that the is_verified returns true if status is 'VERIFIED'.

        self.assertFalse(self.factor.is_verified())
        self.factor._set_properties({'verification_status': 'VERIFIED'})
        self.assertTrue(self.factor.is_verified())

    def test_is_sms(self):
        # Ensure that the is_sms returns true if type is 'SMS'.

        self.assertTrue(self.factor.is_sms())
        self.factor.type = 'google-authenticator'
        self.assertFalse(self.factor.is_sms())

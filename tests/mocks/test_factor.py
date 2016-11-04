from unittest import TestCase
from stormpath.resources.factor import Factor, FactorList
from stormpath.resources.challenge import Challenge
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
                'type': 'SMS'
            })
        self.factors = FactorList(client=self.client, href='test/factors')
        self.challenge = Challenge(
            self.client,
            properties={
                'href': '/challenges/challenge_id',
                'factor': self.factor
            })

    @patch('stormpath.resources.base.CollectionResource.create')
    def test_create_challenge_is_popped(self, create):
        # Ensure that challenge is popped from data if we wish to challenge
        # the factor later.

        create.return_value = self.factor

        properties = {
            'type': 'SMS',
            'phone': {'number': '+666'},
            'challenge': {'message': '${code}'}
        }

        self.factors.create(properties=properties.copy(), challenge=False)

        properties.pop('challenge')
        create.assert_called_once_with(
            properties, challenge=False, expand=None)

    @patch('stormpath.data_store.DataStore.update_resource')
    def test_challenge_factor_correct_params(self, update):
        # Ensure that message is passed as dict and that update href is
        # properly appended.

        update.return_value = self.challenge

        self.factor._set_properties({'most_recent_challenge': self.challenge})
        self.factor.challenge_factor(message='This is your message ${code}.')

        update.assert_called_once_with(
            '/factors/factor_id/challenges',
            {'message': 'This is your message ${code}.'})

    @patch('stormpath.data_store.DataStore.update_resource')
    def test_challenge_factor_google_authenticator_code(self, update):
        # Ensure that the code parameter is present when challenging
        # a google-authenticator factor.

        update.return_value = self.challenge

        self.factor._set_properties({'most_recent_challenge': self.challenge})
        self.factor.type = 'google-authenticator'

        # Ensure that the missing code will raise an error.
        with self.assertRaises(ValueError) as error:
            self.factor.challenge_factor()
        self.assertEqual(
            error.exception.message, 'When challenging a ' +
            'google-authenticator factor, activation code must be provided.')

        # Ensure that the code will challenge the factor.
        self.factor.challenge_factor(code='123456')

        # Ensure that challenge_factor does not create a request if the code
        # is missing.
        update.assert_called_once_with(
            '/factors/factor_id/challenges',
            {'message': 'Your verification code is ${code}',
             'code': '123456'})

    @patch('stormpath.data_store.DataStore.update_resource')
    def test_challenge_factor_message_default(self, update):
        # Ensure that the default message is properly set when challenging
        # factor.

        update.return_value = self.challenge

        self.factor._set_properties({'most_recent_challenge': self.challenge})
        self.factor.challenge_factor()

        update.assert_called_once_with(
            '/factors/factor_id/challenges',
            {'message': 'Your verification code is ${code}'})

    @patch('stormpath.data_store.DataStore.update_resource')
    def test_challenge_factor_message_custom(self, update):
        # Ensure that the default message is properly overridden when
        # challenging factor.

        update.return_value = self.challenge

        self.factor._set_properties({'most_recent_challenge': self.challenge})
        self.factor.challenge_factor(message='This is your message ${code}.')

        update.assert_called_once_with(
            '/factors/factor_id/challenges',
            {'message': 'This is your message ${code}.'})

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

        self.factors.create(properties=properties.copy(), challenge=True)
        create.assert_called_once_with(
            properties, challenge=True, expand=None)

    @patch('stormpath.resources.base.CollectionResource.create')
    def test_create_factor_message_default_with_challenge(self, create):
        # Ensure that the default message is properly set, even if message
        # is missing from challenge dict.

        properties = {
            'type': 'SMS',
            'phone': {'number': '+666'},
            'challenge': {}
        }
        self.factors.create(properties=properties.copy(), challenge=True)

        called_with_properties = {
            'type': 'SMS',
            'phone': {'number': '+666'},
            'challenge': {'message': 'Your verification code is ${code}'}
        }
        create.assert_called_once_with(
            called_with_properties, challenge=True, expand=None)

    @patch('stormpath.resources.base.CollectionResource.create')
    def test_create_factor_message_default_without_challenge(self, create):
        # Ensure that the default message is properly set, even if challenge
        # is missing from properties.

        properties = {
            'type': 'SMS',
            'phone': {'number': '+666'}
        }
        self.factors.create(properties=properties.copy(), challenge=True)

        called_with_properties = {
            'type': 'SMS',
            'phone': {'number': '+666'},
            'challenge': {'message': 'Your verification code is ${code}'}
        }
        create.assert_called_once_with(
            called_with_properties, challenge=True, expand=None)

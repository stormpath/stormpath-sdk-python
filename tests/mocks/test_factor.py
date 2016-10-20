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
                'name': 'factor'
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
            "type": "SMS",
            "phone": {"number": "+666"},
            "challenge": {"message": "${code}"}
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
        self.factor.challenge_factor('This is your message ${code}.')

        update.assert_called_once_with(
            '/factors/factor_id/challenges',
            {'message': 'This is your message ${code}.'})

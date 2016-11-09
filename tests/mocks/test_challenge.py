import json
from unittest import TestCase
from stormpath.resources.account import Account
from stormpath.resources.factor import Factor
from stormpath.resources.challenge import Challenge
from stormpath.data_store import DataStore
from stormpath.http import HttpExecutor

try:
    from mock import MagicMock, patch
except ImportError:
    from unittest.mock import MagicMock, patch


class TestChallenge(TestCase):

    @patch('stormpath.http.Session')
    def setUp(self, Session):

        # Set mock.
        self.request_mock = Session.return_value.request
        self.request_mock.return_value = MagicMock()

        ex = HttpExecutor('https://api.stormpath.com/v1', ('user', 'pass'))
        self.client = MagicMock(BASE_URL='http://example.com')
        self.data_store = DataStore(ex)
        self.client.data_store = self.data_store
        self.account = Account(
            self.client,
            properties={
                'href': 'http://example.com/account',
                'username': 'username',
                'given_name': 'given_name',
                'surname': 'surname',
                'email': 'test@example.com',
                'password': 'Password123!'})
        self.factor = Factor(
            self.client,
            properties={
                'href': '/factors/factor_id',
                'name': 'factor'
            })
        self.challenge = Challenge(
            self.client,
            properties={
                'href': '/challenges/challenge_id',
                'factor': self.factor,
                'account': self.account
            })

    def test_submit(self):
        # Ensure that submitting a challenge will produce a proper request.

        # Set activation code and most recent challenge
        data = {'code': '000000'}
        self.factor._set_properties({'most_recent_challenge': self.challenge})
        self.factor.most_recent_challenge.submit(data['code'])

        # Ensure that a POST request was made to submit the challenge,
        # and a GET request to refresh the instance.
        self.assertEqual(self.request_mock.call_count, 2)
        call1 = self.request_mock._mock_call_args_list[0]
        call2 = self.request_mock._mock_call_args_list[1]

        call_params = (
            ('POST', 'https://api.stormpath.com/v1/challenges/challenge_id'),
            {
                'headers': None,
                'allow_redirects': False,
                'params': None,
                'data': json.dumps(data)
            }
        )
        self.assertEqual(tuple(call1), call_params)

        call_params = (
            ('GET', 'https://api.stormpath.com/v1/challenges/challenge_id'),
            {
                'headers': None,
                'allow_redirects': False,
                'params': None,
                'data': None
            }
        )
        self.assertEqual(tuple(call2), call_params)

    def test_status_successful(self):
        # Ensure that successful status method is properly working.

        self.challenge._set_properties({'status': 'SUCCESS'})
        self.assertTrue(self.challenge.is_successful())

    def test_status_waiting(self):
        # Ensure that waiting status method is properly working.

        # Ensure that WAITING_FOR_PROVIDER (waiting for Twilio to send it out)
        # will return True on is_waiting().
        self.challenge._set_properties({'status': 'WAITING_FOR_PROVIDER'})
        self.assertTrue(self.challenge.is_waiting())

        # Ensure that WAITING_FOR_VALIDATION (waiting for user to submit code)
        # will return True on is_waiting().
        self.challenge._set_properties({'status': 'WAITING_FOR_VALIDATION'})
        self.assertTrue(self.challenge.is_waiting())

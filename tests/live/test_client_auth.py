"""Live tests of client authentication against the Stormpath service API."""

from os import environ

from stormpath.client import Client
from stormpath.error import Error

from .base import LiveBase


class TestAuth(LiveBase):

    def test_basic_authentication_succeeds(self):
        client = Client(
            id=self.api_key_id,
            secret=self.api_key_secret,
            scheme='basic')
        # force the SDK to make a call to the server
        list(client.applications)

    def test_basic_authentication_with_api_key_succeeds(self):
        api_key = {
            'api_key_id': self.api_key_id,
            'api_key_secret': self.api_key_secret
        }
        client = Client(
            api_key=api_key,
            scheme='basic')
        # force the SDK to make a call to the server
        list(client.applications)

    def test_basic_authentication_w_api_key_id_n_api_key_secret_succeeds(self):
        client = Client(
            api_key_id=self.api_key_id,
            api_key_secret=self.api_key_secret,
            scheme='basic')
        # force the SDK to make a call to the server
        list(client.applications)

    def test_basic_authentication_fails(self):
        client = Client(
            id=self.api_key_id + 'x',
            secret=self.api_key_secret + 'x',
            scheme='basic')

        # force the SDK to make a call to the server
        with self.assertRaises(Error):
            list(client.applications)

    def test_digest_authentication_succeeds(self):
        client = Client(
            id=self.api_key_id,
            secret=self.api_key_secret,
            scheme='SAuthc1')
        # force the SDK to make a call to the server
        client.applications

    def test_digest_authentication_fails(self):
        client = Client(
            id=self.api_key_id + 'x',
            secret=self.api_key_secret + 'x',
            scheme='SAuthc1')

        # force the SDK to make a call to the server
        with self.assertRaises(Error):
            list(client.applications)

    def test_load_from_environment_variables(self):
        client = Client()
        for app in client.applications:
            self.assertTrue(app.href)

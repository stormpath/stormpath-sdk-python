"""Base classes for the live tests against the Stormpath API service."""

from os import getenv
from time import sleep
from unittest import TestCase
from uuid import uuid4

from pydispatch import dispatcher

from stormpath.client import Client
from stormpath.resources.base import SIGNAL_RESOURCE_CREATED


def sleep_receiver_function(signal, sender, data, params):
    """Sleeps for one second.

    This is used as receiver of a signal
    (eg. when resource is created).
    """
    sleep(1)


class LiveBase(TestCase):
    """Picks up Stormpath API key/secret from environment.

    Environment variables used are the same as if using environment variables
    for API authentication in actual use:

        * STORMPATH_API_KEY_ID
        * STORMPATH_API_KEY_SECRET

    If these variables are not present in the environment, the tests will
    complain immediately instead of throwing cryptic "Invalid API key"
    error message from the service.
    """

    @classmethod
    def setUpClass(cls):
        cls.api_key_id = getenv('STORMPATH_API_KEY_ID')
        cls.api_key_secret = getenv('STORMPATH_API_KEY_SECRET')
        if not cls.api_key_id or not cls.api_key_secret:
            raise ValueError('STORMPATH_API_KEY_ID or '
                'STORMPATH_API_KEY_SECRET not provided')

        # This will call sleep function on every resource creation.
        # That is done to prevent random test failures
        # (https://github.com/stormpath/stormpath-sdk-python/issues/149).
        dispatcher.connect(sleep_receiver_function, signal=SIGNAL_RESOURCE_CREATED)


class AuthenticatedLiveBase(LiveBase):
    AUTH_SCHEME = 'basic'
    TEST_PREFIX = 'stormpath-sdk-python-test'

    def setUp(self):
        self.client = Client(id=self.api_key_id, secret=self.api_key_secret, scheme=self.AUTH_SCHEME)
        self.prefix = '{}-{}'.format(self.TEST_PREFIX, uuid4().hex)

    def get_random_name(self):
        return '{}-{}'.format(self.prefix, uuid4().hex)

    def clear_cache(self):
        for cache in self.client.data_store.cache_manager.caches.values():
            cache.clear()


class SingleApplicationBase(AuthenticatedLiveBase):

    def setUp(self):
        super(SingleApplicationBase, self).setUp()
        self.deletes = []
        self.app_name = self.get_random_name()
        self.app = self.client.applications.create({
            'name': self.app_name,
            'description': 'test app'
        }, create_directory=self.app_name)
        self.dir = self.app.default_account_store_mapping.account_store

    def tearDown(self):
        self.dir.delete()
        self.app.delete()
        for r in self.deletes:
            r.delete()


class AccountBase(SingleApplicationBase):

    def create_account(self, coll, username=None, email=None, password=None,
            custom_data=None, given_name=None, surname=None):
        if username is None:
            username = self.get_random_name()
        if email is None:
            email = username + '@example.com'
        if given_name is None:
            given_name = 'Given ' + username
        if surname is None:
            surname = 'Sur ' + username
        if password is None:
            password = 'W00t123!' + username

        props = {
            'username': username,
            'email': email,
            'given_name': given_name,
            'surname': surname,
            'password': password,
        }

        if custom_data:
            props['custom_data'] = custom_data

        account = coll.create(props)
        return username, account


class ApiKeyBase(AccountBase):

    def create_api_key(self, acc):
        return acc.api_keys.create()


class SignalReceiver(object):
    received_signals = None

    def signal_created_receiver_function(self, signal, sender, data, params):
        if self.received_signals is None:
            self.received_signals = []
        self.received_signals.append((sender, data, params))

    def signal_updated_receiver_function(self, signal, sender, href, properties):
        if self.received_signals is None:
            self.received_signals = []
        self.received_signals.append((sender, href, properties))

    def signal_deleted_receiver_function(self, signal, sender, href):
        if self.received_signals is None:
            self.received_signals = []
        self.received_signals.append((sender, href))

"""Live tests of DataStore functionality."""


from unittest import TestCase, main
try:
    from mock import MagicMock
except ImportError:
    from unittest.mock import MagicMock

from stormpath.cache.null_cache_store import NullCacheStore
from stormpath.data_store import DataStore
from stormpath.http import HttpExecutor

from .base import SingleApplicationBase


class TestLiveDataStore(SingleApplicationBase):
    """Assert the DataStore works as expected."""

    def setUp(self):
        super(TestLiveDataStore, self).setUp()
        self.executor = HttpExecutor(
            base_url = 'https://api.stormpath.com/v1',
            auth = (self.api_key_id, self.api_key_secret),
        )

    def test_get_resource(self):
        data_store = DataStore(executor=self.executor)
        self.assertIsInstance(data_store.get_resource(self.app.href), dict)

        acc = self.app.accounts.create({
            'given_name': 'Randall',
            'surname': 'Degges',
            'email': '{}@example.com'.format(self.get_random_name()),
            'password': 'wootILOVEc00kies!!<33',
        })
        key = acc.api_keys.create()
        self.assertIsInstance(key.id, str)

        data_store = DataStore(executor=self.executor)
        data = data_store.get_resource(self.app.href + '/apiKeys', {'id': key.id})
        self.assertIsInstance(data, dict)
        self.assertEqual(data['items'][0]['id'], key.id)

        data_store = DataStore(executor=self.executor)
        data = data_store.get_resource(self.app.tenant.href + '/applications')
        self.assertIsInstance(data, dict)

        hrefs = [data['items'][i]['href'] for i in range(len(data['items']))]
        self.assertTrue(self.app.href in hrefs)


class TestDataStoreWithMemoryCache(TestCase):

    def test_get_resource_is_cached(self):
        ex = MagicMock()
        ds = DataStore(ex)

        ex.get.return_value = {
            'href': 'http://example.com/accounts/FOO',
            'name': 'Foo',
        }

        # make the request twice
        ds.get_resource('http://example.com/accounts/FOO')
        ds.get_resource('http://example.com/accounts/FOO')

        ex.get.assert_called_once_with('http://example.com/accounts/FOO',
            params=None)

    def test_get_resource_api_keys_is_cached(self):

        ex = MagicMock()
        ds = DataStore(ex)

        ex.get.return_value = {
            'href':
                'https://www.example.com/applications/APPLICATION_ID/apiKeys',
            'items': [
                {
                    'href': 'http://example.com/apiKeys/KEY_ID',
                    'id': 'KEY_ID',
                    'secret': 'KEY_SECRET'
                }
            ]
        }

        ds.get_resource(
            'https://www.example.com/applications/APPLICATION_ID/apiKeys',
            {'id': 'KEY_ID'})

        ex.get.assert_called_once_with(
            'https://www.example.com/applications/APPLICATION_ID/apiKeys',
            params={'id': 'KEY_ID'})

        self.assertEqual(
            ds._cache_get('http://example.com/apiKeys/KEY_ID'),
            {
                'secret': 'KEY_SECRET',
                'href': 'http://example.com/apiKeys/KEY_ID',
                'id': 'KEY_ID'
            })


class TestDataStoreWithNullCache(TestCase):
    def test_get_resource_is_not_cached(self):
        ex = MagicMock()
        ds = DataStore(
            ex, {'regions': {'accounts': {'store': NullCacheStore}}})

        ex.get.return_value = {
            'href': 'http://example.com/accounts/FOO',
            'name': 'Foo',
        }

        # make the request twice
        ds.get_resource('http://example.com/accounts/FOO')
        ds.get_resource('http://example.com/accounts/FOO')

        self.assertEqual(ex.get.call_count, 2)


if __name__ == '__main__':
    main()

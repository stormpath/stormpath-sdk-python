from unittest import TestCase, main
try:
    from mock import patch, call, MagicMock
except ImportError:
    from unittest.mock import patch, call, MagicMock

from stormpath.data_store import DataStore


@patch('stormpath.data_store.CacheManager')
class TestDataStore(TestCase):

    def test_cache_creation_with_global_store(self, CacheManager):
        store = MagicMock()
        ds = DataStore(MagicMock(), {'store': store})

        expected = [call(region, store=store) for region in ds.CACHE_REGIONS]

        self.assertEqual(CacheManager.return_value.create_cache.call_args_list,
            expected)

    def test_get_cache_no_cache(self, CacheManager):
        ds = DataStore(MagicMock())

        c = ds._get_cache('invalid')

        # make sure the methods exist and do nothing
        self.assertEqual(c.get(), None)
        c.put()
        c.delete()

    def test_get_cache_parse_instance_href(self, CacheManager):
        ds = DataStore(MagicMock())

        get_cache = CacheManager.return_value.get_cache

        c = ds._get_cache('https://www.example.com/accounts/ACCOUNTID')
        self.assertTrue(c, get_cache.return_value)
        get_cache.assert_called_once_with('accounts')

    def test_get_cache_parse_custom_data_href(self, CacheManager):
        ds = DataStore(MagicMock())

        get_cache = CacheManager.return_value.get_cache

        c = ds._get_cache(
            'https://www.example.com/accounts/ACCOUNTID/customData')
        self.assertTrue(c, get_cache.return_value)
        get_cache.assert_called_once_with('customData')

    def test_uncache_custom_data_key_uncaches_custom_data(self, CacheManager):
        ds = DataStore(MagicMock())

        get_cache = CacheManager.return_value.get_cache

        ds.uncache_resource(
            'https://www.example.com/accounts/ACCOUNTID/customData/KEY')
        get_cache.assert_called_once_with('customData')

    def test_recursive_cache_put(self, CacheManager):
        ds = DataStore(MagicMock())

        data = {
            'href': 'http://example.com/accounts/FOO',
            'name': 'Foo',
            'groups': {
                'href': 'http://example.com/accounts/FOO/groups',
                'items': [
                    {
                        'href': 'http://example.com/groups/G1',
                        'name': 'Foo Group 1',
                    },
                    {
                        'href': 'http://example.com/groups/G2',
                        'name': 'Foo Group 2',
                    }
                ]
            },
            'directory': {
                'href': 'http://example.com/directories/BAR',
                'name': 'Directory',
            }
        }

        ds._cache_put('http://example.com/accounts/FOO', data=data)

        put = CacheManager.return_value.get_cache.return_value.put

        expected = sorted([
            call('http://example.com/groups/G1', {
                'href': 'http://example.com/groups/G1',
                'name': 'Foo Group 1'
            }, new=True),
            call('http://example.com/groups/G2', {
                'href': 'http://example.com/groups/G2',
                'name': 'Foo Group 2'
            }, new=True),
            call('http://example.com/directories/BAR', {
                'href': 'http://example.com/directories/BAR',
                'name': 'Directory'
            }, new=True),
            call('http://example.com/accounts/FOO', {
                'href': 'http://example.com/accounts/FOO',
                'name': 'Foo',
                'groups': {
                    'href': 'http://example.com/accounts/FOO/groups',
                    'items': [
                        {'href': 'http://example.com/groups/G1'},
                        {'href': 'http://example.com/groups/G2'},
                    ]
                },
                'directory': {
                    'href': 'http://example.com/directories/BAR'
                }
            }, new=True)
        ], key=lambda c: c[1][0])

        actual = sorted(put.call_args_list, key=lambda c: c[0][0])
        self.assertEqual(actual, expected)


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

if __name__ == '__main__':
    main()

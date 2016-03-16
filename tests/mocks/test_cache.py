from unittest import TestCase, main
try:
    from mock import patch, MagicMock
except ImportError:
    from unittest.mock import patch, MagicMock

from stormpath.cache.entry import CacheEntry
from stormpath.cache.stats import CacheStats
from stormpath.cache.cache import Cache
from stormpath.cache.manager import CacheManager
from stormpath.cache.memory_store import MemoryStore
from stormpath.cache.redis_store import RedisStore
from stormpath.cache.memcached_store import MemcachedStore, \
    json_deserializer, json_serializer


class TestCacheEntry(TestCase):

    def setUp(self):
        from datetime import datetime as real_datetime
        self.hour_before = real_datetime(2013, 1, 1, 9, 30, 0, 0)
        self.minute_before = real_datetime(2013, 1, 1, 10, 29, 0, 0)
        self.now = real_datetime(2013, 1, 1, 10, 30, 0, 0)

    @patch('stormpath.cache.entry.datetime')
    def test_entry_init_with_default_values(self, datetime):
        e = CacheEntry('foo')

        self.assertEqual(e.created_at, datetime.utcnow.return_value)
        self.assertEqual(e.last_accessed_at, datetime.utcnow.return_value)

    @patch('stormpath.cache.entry.datetime')
    def test_entry_init_with_custom_values(self, datetime):
        e = CacheEntry('foo', created_at=self.hour_before,
            last_accessed_at=self.minute_before)
        self.assertEqual(e.created_at, self.hour_before)
        self.assertEqual(e.last_accessed_at, self.minute_before)

    @patch('stormpath.cache.entry.datetime')
    def test_touch_updates_last_accessed(self, datetime):
        datetime.utcnow.return_value = self.now

        e = CacheEntry('foo', created_at=self.minute_before,
            last_accessed_at=self.minute_before)

        e.touch()
        self.assertEqual(e.last_accessed_at, self.now)

    @patch('stormpath.cache.entry.datetime')
    def test_is_expired_checks_ttl_tti(self, datetime):
        datetime.utcnow.return_value = self.now

        e = CacheEntry('foo', created_at=self.hour_before,
            last_accessed_at=self.minute_before)

        # check ttl
        self.assertTrue(e.is_expired(3600, 24 * 3600))
        self.assertFalse(e.is_expired(3601, 24 * 3600))
        # check tti
        self.assertTrue(e.is_expired(24 * 3600, 60))
        self.assertFalse(e.is_expired(24 * 3600, 61))

    def test_parse(self):
        e = CacheEntry.parse({
            'value': 'foo',
            'created_at': '2013-01-01 09:30:00.0',
            'last_accessed_at': '2013-01-01 10:29:00.0'
        })

        self.assertEqual(e.value, 'foo')
        self.assertEqual(e.created_at, self.hour_before)
        self.assertEqual(e.last_accessed_at, self.minute_before)

    @patch('stormpath.cache.entry.datetime')
    def test_parse_invalid_dates(self, datetime):
        datetime.strptime.side_effect = ValueError

        e = CacheEntry.parse({'value': 'foo'})

        self.assertEqual(e.value, 'foo')
        self.assertEqual(e.created_at, datetime.utcnow.return_value)
        self.assertEqual(e.last_accessed_at, datetime.utcnow.return_value)

    def test_to_dict(self):
        e = CacheEntry('foo', created_at=self.hour_before,
            last_accessed_at=self.minute_before)

        data = e.to_dict()

        self.assertEqual(data['value'], 'foo')
        self.assertEqual(data['created_at'],
            '2013-01-01 09:30:00.000000')
        self.assertEqual(data['last_accessed_at'],
            '2013-01-01 10:29:00.000000')


class CacheStatsTest(TestCase):

    def test_everything(self):
        s = CacheStats()

        s.put()
        self.assertEqual(s.puts, 1)
        self.assertEqual(s.size, 1)

        s.put(new=False)
        self.assertEqual(s.puts, 2)

        s.hit()
        self.assertEqual(s.hits, 1)

        s.miss()
        self.assertEqual(s.misses, 1)

        s.miss(expired=True)
        self.assertEqual(s.misses, 2)
        self.assertEqual(s.expirations, 1)

        s.delete()
        self.assertEqual(s.size, 0)

        s.put()
        self.assertEqual(s.size, 1)
        s.clear()
        self.assertEqual(s.size, 0)

        # puts hits misses expirations size
        self.assertEqual(s.summary, (3, 1, 2, 1, 0))


@patch('stormpath.cache.cache.CacheStats')
class TestCache(TestCase):

    def test_cache_init_creates_store_and_stats(self, CacheStats):
        store = MagicMock()
        c = Cache(store=store, ttl=100, tti=10,
                store_opts={'foo': 1, 'bar': 2, 'baz': 3})

        CacheStats.assert_called_once_with()
        store.assert_called_once_with(foo=1, bar=2, baz=3)

        self.assertEqual(c.store, store.return_value)
        self.assertEqual(c.stats, CacheStats.return_value)

    def test_cache_get_existing_key(self, CacheStats):
        store = MagicMock()
        store.__getitem__.return_value.is_expired.return_value = False

        c = Cache(store=MagicMock(return_value=store))
        foo = c.get('foo')

        store.__getitem__.assert_called_once_with('foo')
        CacheStats.return_value.hit.assert_called_once_with()
        store.__getitem__.return_value.touch.assert_called_once_with()
        self.assertEqual(foo, store.__getitem__.return_value.value)

    def test_cache_get_expired_key(self, CacheStats):
        store = MagicMock()
        store.__getitem__.return_value.is_expired.return_value = True

        c = Cache(store=MagicMock(return_value=store))
        foo = c.get('foo')

        store.__delitem__.assert_called_once_with('foo')
        CacheStats.return_value.miss.assert_called_once_with(expired=True)
        self.assertIsNone(foo)

    def test_cache_get_missing_key(self, CacheStats):
        store = MagicMock()
        store.__getitem__.return_value = None

        c = Cache(store=MagicMock(return_value=store))
        foo = c.get('foo')

        CacheStats.return_value.miss.assert_called_once_with()
        self.assertIsNone(foo)

    @patch('stormpath.cache.cache.CacheEntry')
    def test_cache_put(self, CacheEntry, CacheStats):
        store = MagicMock()

        c = Cache(store=MagicMock(return_value=store))
        c.put('foo', 'Value Of Foo', new=True)

        CacheEntry.assert_called_once_with('Value Of Foo')

        store.__setitem__.assert_called_once_with('foo',
            CacheEntry.return_value)
        CacheStats.return_value.put.assert_called_once_with(new=True)

    def test_cache_delete(self, CacheStats):
        store = MagicMock()

        c = Cache(store=MagicMock(return_value=store))
        c.delete('foo')

        store.__delitem__.assert_called_once_with('foo')
        CacheStats.return_value.delete.assert_called_once_with()

    def test_cache_size(self, CacheStats):
        store = MagicMock()
        c = Cache(store=MagicMock(return_value=store))
        s = c.size

        store.__len__.assert_called_once_with()
        self.assertEqual(s, store.__len__.return_value)

    def test_cache_clear(self, CacheStats):
        store = MagicMock()
        c = Cache(store=MagicMock(return_value=store))
        c.clear()

        store.clear.assert_called_once_with()
        CacheStats.return_value.clear.assert_called_once_with()

    def test_cache_max_entries(self, CacheStats):
        cache = Cache(store=MemoryStore, store_opts={'max_entries': 2})
        for i in range(1,10):
            cache.put(i, i)
        self.assertEqual(2, len(cache.store))
        self.assertEqual(list(cache.store.store.keys()), [8,9])

    def test_cache_does_not_allow_max_entries_to_fall_bellow_one(self, CacheStats):
        self.assertRaises(
                ValueError,
                Cache,
                store=MemoryStore,
                store_opts={'max_entries': 0})


@patch('stormpath.cache.manager.Cache')
class TestCacheManager(TestCase):

    def test_create_get_cache(self, Cache):
        m = CacheManager()

        m.create_cache('region', foo=1, bar=2, baz=3)
        Cache.assert_called_once_with(foo=1, bar=2, baz=3)

        c = m.get_cache('region')
        self.assertEqual(c, Cache.return_value)

    def test_stats(self, Cache):

        m = CacheManager()
        m.create_cache('foo')
        m.create_cache('bar')

        self.assertEqual(m.stats, {'foo': Cache.return_value.stats,
            'bar': Cache.return_value.stats})


class MemoryStoreTest(TestCase):

    def test_everything(self):
        s = MemoryStore()
        self.assertEqual(len(s), 0)

        self.assertIsNone(s['foo'])

        s['foo'] = 'Value Of Foo'
        self.assertEqual(len(s), 1)
        self.assertEqual(s['foo'], 'Value Of Foo')

        del s['foo']
        self.assertEqual(len(s), 0)

        del s['nonexistent']  # shouldn't raise anything

        s['bar'] = 1
        s.clear()
        self.assertEqual(len(s), 0)


class TestRedisStore(TestCase):

    class Redis(object):
        def __init__(self, *args, **kwargs):
            self.data = {}

        def get(self, key):
            return self.data.get(key)

        def setex(self, key, data, ttl):
            self.data[key] = data

        def delete(self, key):
            if key in self.data:
                del self.data[key]

        def flushdb(self):
            self.data = {}

        def dbsize(self):
            return len(self.data)

    def test_redis_not_available(self):
        # make sure redis is not available
        with patch.dict('sys.modules', {'redis': object()}):
            with self.assertRaises(RuntimeError):
                RedisStore()

    def test_everything(self):
        # make sure our mocked redis is available
        with patch.dict('sys.modules', {'redis': MagicMock(Redis=self.Redis)}):
            s = RedisStore()

        self.assertEqual(len(s), 0)

        self.assertIsNone(s['foo'])

        s['foo'] = CacheEntry('Value Of Foo')
        self.assertEqual(len(s), 1)
        self.assertEqual(s['foo'].value, 'Value Of Foo')

        del s['foo']
        self.assertEqual(len(s), 0)

        del s['nonexistent']  # shouldn't raise anything

        s['bar'] = CacheEntry(1)
        s.clear()
        self.assertEqual(len(s), 0)


class TestMemcachedStore(TestCase):

    class Memcache(object):
        def __init__(self, *args, **kwargs):
            self.data = {}

        def get(self, key):
            data, flags = self.data.get(key)
            data = json_deserializer(key, data, flags)
            return data

        def set(self, key, entry, expire):
            data, flags = json_serializer(key, entry)
            self.data[key] = (data, flags)

        def delete(self, key):
            if key in self.data:
                del self.data[key]

        def flush_all(self):
            self.data = {}

        def stats(self):
            return {'curr_items': len(self.data)}

    def test_pymemcache_not_available(self):
        # make sure pymemcache is not available
        with patch.dict('sys.modules', {'pymemcache': object(), 'pymemcache.client': object()}):
            with self.assertRaises(RuntimeError):
                MemcachedStore()

    def test_everything(self):
        with patch.dict('sys.modules', {'pymemcache': object(), 'pymemcache.client': MagicMock(Client=self.Memcache)}):
            s = MemcachedStore()

        self.assertEqual(len(s), 0)
        self.assertIsNone(s['foo'])

        s['foo'] = CacheEntry('Value Of Foo')
        self.assertEqual(len(s), 1)
        self.assertEqual(s['foo'].value, 'Value Of Foo')

        del s['foo']
        self.assertEqual(len(s), 0)

        del s['nonexistent']  # shouldn't raise anything

        s['bar'] = CacheEntry(1)
        s.clear()
        self.assertEqual(len(s), 0)


if __name__ == '__main__':
    main()

"""A redis cache backend."""


from json import (
    dumps,
    loads,
)

from .entry import CacheEntry


class RedisStore(object):
    """Caching implementation that uses Redis as data storage."""

    DEFAULT_TTL = 5 * 60  # seconds

    def __init__(self, host='localhost', port=6379, db=0,
            ttl=DEFAULT_TTL):
        self.ttl = ttl
        try:
            from redis import Redis
        except ImportError:
            raise RuntimeError('Redis support is not available. Run "pip install redis".')

        self.redis = Redis(host=host, port=port, db=db)

    def __getitem__(self, key):
        entry = self.redis.get(key)
        if entry is None:
            return None

        entry = loads(entry.decode('utf-8'))
        return CacheEntry.parse(entry)

    def __setitem__(self, key, entry):
        data = dumps(entry.to_dict()).encode('utf-8')
        self.redis.setex(key, data, self.ttl)

    def __delitem__(self, key):
        self.redis.delete(key)

    def clear(self):
        self.redis.flushdb()

    def __len__(self):
        return self.redis.dbsize()

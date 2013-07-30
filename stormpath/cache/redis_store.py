import json
from .entry import CacheEntry


class RedisStore(object):

    def __init__(self, host='localhost', port=6379, db=0):
        try:
            from redis import Redis
        except ImportError:
            raise RuntimeError('Redis support is not available')
        self.redis = Redis(host=host, port=port, db=db)

    def __getitem__(self, key):
        entry = self.redis.get(key)
        if entry is None:
            return None

        entry = json.loads(entry.decode('utf-8'))
        return CacheEntry.parse(entry)

    def __setitem__(self, key, entry):
        data = json.dumps(entry.to_dict()).encode('utf-8')
        self.redis.set(key, data)

    def __delitem__(self, key):
        self.redis.delete(key)

    def clear(self):
        self.redis.flushdb()

    def __len__(self):
        return self.redis.dbsize()

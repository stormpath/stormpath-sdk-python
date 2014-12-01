"""A redis cache backend."""


from json import (
    dumps,
    loads,
)

from .entry import CacheEntry


class RedisStore(object):
    """Caching implementation that uses Redis as data storage.

    :param host: String representing the hostname or IP of the Redis server

    :param port: Port number (int) on which the Redis server is listening

    :param db: DB querystring option (Default: 0, e.g. redis://localhost?db=0)

    :param password: Redis server password (Default: No Password)

    :param socket_timeout: Connection timeout to Redis server

    :param connection_pool: ConnectionPool for Redis instance (See redis-py docs)

    :param charset: Default character set

    :param errors: Default error settings

    :param decode_responses: Default: False (values in message dictionaries will be
        byte strings (str on Python 2, bytes on Python 3)

    :param unix_socket_path: Socker path. For using UnixDomainSocketConnection
        (see redis-py docs for more details)

    :param ttl: Default TTL
    """

    DEFAULT_TTL = 5 * 60  # seconds

    def __init__(self, host='localhost', port=6379, db=0, password=None,
            socket_timeout=None, connection_pool=None, charset='utf-8',
            errors='strict', decode_responses=False, unix_socket_path=None,
            ttl=DEFAULT_TTL):
        self.ttl = ttl
        try:
            from redis import Redis
        except ImportError:
            raise RuntimeError('Redis support is not available. Run "pip install redis".')

        self.redis = Redis(host=host, port=port, db=db,
                password=password, socket_timeout=socket_timeout,
                connection_pool=connection_pool, charset=charset,
                errors=errors, decode_responses=decode_responses,
                unix_socket_path=unix_socket_path)

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

"""A memcached cache backend."""

import socket
from functools import wraps
from json import (
    dumps,
    loads,
)

from .entry import CacheEntry

STR_VALUE = 1
JSON_VALUE = 2


def json_serializer(key, value):
    if isinstance(value, str):
        return value, STR_VALUE
    return dumps(value.to_dict()).encode('utf-8'), JSON_VALUE


def json_deserializer(key, value, flags):
    if flags == STR_VALUE:
        return value
    if flags == JSON_VALUE:
        return loads(value.decode('utf-8'))
    raise Exception("Unknown serialization format")


def memcache_error_handling(f):
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        try:
            ret = f(self, *args, **kwargs)
        except Exception:
            return None
        return ret
    return wrapper


class MemcachedStore(object):
    """Caching implementation that uses Memcached as data storage.

    :param host: String representation of hostname or IP of the memcached server

    :param port: Port number (int) on which the memcached server is listening

    :param connect_timeout: optional float, seconds to wait for a connection to
        the memcached server. Defaults to "forever" (uses the underlying
        default socket timeout, which can be very long)

    :param timeout: optional float, seconds to wait for send or recv calls on
        the socket connected to memcached. Defaults to "forever" (uses the
        underlying default socket timeout, which can be very long).

    :param no_delay: optional bool, set the TCP_NODELAY flag, which may help
        with performance in some cases. Defaults to False.

    :param ignore_exc: optional bool, True to cause the "get", "gets",
        "get_many" and "gets_many" calls to treat any errors as cache
        misses. Defaults to True. Ie. if the cache is failing use the
        Stormpath API.

    :param socket_module: socket module to use, e.g. gevent.socket. Defaults to
        the standard library's socket module.

    :param key_prefix: Prefix of key. You can use this as namespace. Defaults
        to b''.

    """

    DEFAULT_TTL = 5 * 60  # seconds

    def __init__(self, host='localhost', port=11211,
            connect_timeout=None, timeout=None,
            no_delay=False, ignore_exc=True,
            key_prefix=b'', socket_module=socket, ttl=DEFAULT_TTL):
        self.ttl = ttl

        try:
            from pymemcache.client import Client as Memcache
        except ImportError:
            raise RuntimeError('Memcached support is not available. Run "pip install pymemcache".')

        self.memcache = Memcache(
                (host, port),
                serializer=json_serializer,
                deserializer=json_deserializer,
                connect_timeout=connect_timeout,
                timeout=timeout,
                socket_module=socket_module,
                no_delay=no_delay,
                ignore_exc=ignore_exc,
                key_prefix=key_prefix)

    @memcache_error_handling
    def __getitem__(self, key):
        entry = self.memcache.get(key)

        if entry is None:
            return None

        return CacheEntry.parse(entry)

    @memcache_error_handling
    def __setitem__(self, key, entry):
        self.memcache.set(key, entry, expire=self.ttl)

    @memcache_error_handling
    def __delitem__(self, key):
        self.memcache.delete(key)

    @memcache_error_handling
    def clear(self):
        self.memcache.flush_all()

    @memcache_error_handling
    def __len__(self):
        return self.memcache.stats()['curr_items']


"""Cache abstractions."""


from .entry import CacheEntry
from .memory_store import MemoryStore
from .stats import CacheStats


class Cache(object):
    """A unified interface to different implementations of data caching.

    Example of an implementetion is
    :class:`stormpath.cache.memory_store.MemoryStore`.
    It also provides usage statistics with
    :class:`stormpath.cache.stats.CacheStats`.
    """
    DEFAULT_STORE = MemoryStore
    DEFAULT_TTL = 5 * 60  # seconds
    DEFAULT_TTI = 5 * 60  # seconds

    def __init__(self, store=DEFAULT_STORE, ttl=DEFAULT_TTL, tti=DEFAULT_TTI,
            **kwargs):
        self.ttl = ttl
        self.tti = tti
        store_opts = kwargs.get('store_opts', {})
        # pass along max entries only to memory store instances
        if store != MemoryStore:
            store_opts.pop('max_entries', None)
        self.store = store(**store_opts)
        self.stats = CacheStats()

    def get(self, key):
        entry = self.store[key]
        if entry:
            if entry.is_expired(self.ttl, self.tti):
                self.stats.miss(expired=True)
                del self.store[key]

                return None
            else:
                self.stats.hit()
                entry.touch()

                return entry.value
        else:
            self.stats.miss()

            return None

    def put(self, key, value, new=True):
        self.store[key] = CacheEntry(value)
        self.stats.put(new=new)

    def delete(self, key):
        del self.store[key]
        self.stats.delete()

    def clear(self):
        self.store.clear()
        self.stats.clear()

    @property
    def size(self):
        return len(self.store)

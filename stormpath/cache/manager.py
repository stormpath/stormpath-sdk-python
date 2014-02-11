"""Cache manager abstraction."""


from .cache import Cache


class CacheManager(object):
    """Handles all the different caches used by the SDK

    It keeps track which resource belongs to which cache.\
    E.g :class:`stormpath.resources.directory.Directory` resource data is stored
    in :class:`stormpath.cache.memory_store.MemoryStore` while \
    :class:`stormpath.resources.application.Application` resource data is stored
    in :class:`stormpath.cache.redis_store.RedisStore`.
    The CacheManager, along with :class:`stormpath.http.HttpExecutor` is a part
    of the :class:`stormpath.data_store.DataStore`.
    """

    def __init__(self):
        self.caches = {}

    def create_cache(self, region, **options):
        self.caches[region] = Cache(**options)

    def get_cache(self, region):
        return self.caches.get(region)

    @property
    def stats(self):
        return {region: cache.stats for region, cache in self.caches.items()}

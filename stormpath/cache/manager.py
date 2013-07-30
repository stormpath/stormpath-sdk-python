from .cache import Cache


class CacheManager(object):

    def __init__(self):
        self.caches = {}

    def create_cache(self, region, **options):
        self.caches[region] = Cache(**options)

    def get_cache(self, region):
        return self.caches.get(region)

    @property
    def stats(self):
        return {region: cache.stats for region, cache in self.caches.items()}

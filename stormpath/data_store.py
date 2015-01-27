"""Data store abstractions."""


from .cache.manager import CacheManager


class DataStore(object):
    """An intermediary between Resource objects and the data they represent.

    It fetches the data either from the Stormpath service by using
    the :class:`stormpath.http.HttpExecutor` if the cache doesn't already have
    it and caches it by using :class:`stormpath.cache.manager.CacheManager` or
    fetches the data directly from the cache. Those two components are part of
    DataStore but implemented separately with the intent of being easily
    replacable without changing the the rest of the codebase.
    """
    CACHE_REGIONS = (
        'accounts',
        'apiKeys',
        'accountStoreMappings',
        'applications',
        'customData',
        'directories',
        'groups',
        'groupMemberships',
        'tenants',
        'nonces',
    )

    def __init__(self, executor, cache_options=None):
        """
        :param executor: A HTTP request executor,
            like :class:`stormpath.http.HttpExecutor`
        :param cache_options: A dictionary with cache settings.

        Example of a dictionary with all available options::

            {
                'store': MemoryStore,
                'regions': {
                    'applications': {
                        'store': RedisStore,
                        'ttl': 300,
                        'tti': 300,
                        'store_opts': {
                            'host': 'localhost',
                            'port': 6739,
                        },
                    },
                    'directories': {
                        'store': MemoryStore,
                        'ttl': 60,
                    },
                },
            }
        """
        self.cache_manager = CacheManager()
        self.executor = executor

        if cache_options is None:
            cache_options = {}

        for region in self.CACHE_REGIONS:
            opts = cache_options.get(region, {})
            for k, v in cache_options.items():
                if k not in opts and k != 'regions':
                    opts[k] = v

            self.cache_manager.create_cache(region, **opts)

    def _get_cache(self, href):
        class NoCache(object):
            def get(self, *args, **kwargs):
                return None

            def put(self, *args, **kwargs):
                pass

            def delete(self, *args, **kwargs):
                pass

        if '/' not in href:
            return NoCache()

        parts = href.split('/')

        # resource hrefs are in format:
        # ".../resource/resource_uid"
        if parts[-2] in self.CACHE_REGIONS:  # We only care about instances.
            return self.cache_manager.get_cache(parts[-2]) or NoCache()

        # custom data hrefs are in format:
        # ".../resource/resource_uid/customData"
        elif parts[-1] in self.CACHE_REGIONS and parts[-1] == 'customData':
            return self.cache_manager.get_cache(parts[-1]) or NoCache()

        else:
            return NoCache()

    def _cache_get(self, href):
        return self._get_cache(href).get(href)

    def _cache_put(self, href, data, new=True):
        resource_data = {}
        for name, value in data.items():
            if isinstance(value, dict) and 'href' in value:
                v2 = {'href': value['href']}
                if 'items' in value:
                    v2['items'] = []

                    for item in value['items']:
                        self._cache_put(item['href'], item)
                        v2['items'].append({
                            'href': item['href']
                        })
                else:
                    if len(value) > 1:
                        self._cache_put(value['href'], value)
            else:
                v2 = value

            resource_data[name] = v2

        self._get_cache(href).put(href, resource_data, new=new)

    def uncache_resource(self, href):
        """
        Uncaching customData's key should uncache customData.
        """
        if 'customData' in href and not href.endswith('customData'):
            parts = href.split('/')
            href = '/'.join(parts[:-1])

        self._get_cache(href).delete(href)

    def get_resource(self, href, params=None):
        data = self._cache_get(href)
        if data is None:
            data = self.executor.get(href, params=params)
            self._cache_put(href, data)

        return data

    def create_resource(self, href, data, params=None):
        data = self.executor.post(href, data, params=params)
        self._cache_put(href, data)

        return data

    def update_resource(self, href, data):
        data = self.executor.post(href, data)
        self._cache_put(href, data, new=False)

        return data

    def delete_resource(self, href):
        self.executor.delete(href)
        self.uncache_resource(href)

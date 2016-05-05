"""Data store abstractions."""


from .cache.manager import CacheManager


class DataStore(object):
    """
    The DataStore object is an intermediary between Stormpath resources and the
    Stormpath API. It handles fetching Stormpath data from either the Stormpath
    API service, or a cache.

    More info can be found in our documentation:
    http://docs.stormpath.com/python/product-guide/#sdk-concepts

    Examples::

        from stormpath.cache.memory_store import MemoryStore
        from stormpath.cache.redis_store import RedisStore

        data_store = DataStore(executor, {
            'store': MemoryStore,
            'regions': {
                'applications': {
                    'store': RedisStore,
                    'ttl': 300,
                    'tti': 300,
                    'store_opts': {
                        'host': 'localhost',
                        'port': 6739,
                    }
                },
                'directories': {
                    'ttl': 60,
                    'tti': 60,
                }
            }
        })
    """
    CACHE_REGIONS = (
        'accounts',
        'apiKeys',
        'accountStoreMappings',
        'applications',
        'customData',
        'directories',
        'organizations',
        'groups',
        'groupMemberships',
        'tenants',
        'nonces',
    )

    def __init__(self, executor, cache_options=None):
        """
        Initialize the DataStore.

        :param obj executor: An HTTP request executor.
        :type executor: :class:`stormpath.http.HttpExecutor`
        :param cache_options: A dictionary with cache settings.
        :type cache_options: dict or None, optional
        :returns: The initialized DataStore object.
        :rtype: :class:`stormpath.data_store.DataStore`
        """
        self.cache_manager = CacheManager()
        self.executor = executor

        if cache_options is None:
            cache_options = {}

        for region in self.CACHE_REGIONS:
            opts = cache_options.get('regions', {}).get(region, {})
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
        This method will purge a resource from the cache.

        :param str href: The resource href to uncache.

        .. note::
            CustomData is a special case here.  If a developer is deleting only
            a specific CustomData key, we need to delete the entire CustomData
            cache we have, since we only cache CustomData as a whole, and not on
            a per-key basis.

        Examples::

            data_store.uncache_resource('https://api.stormpath.com/v1/accounts/xxx')
            data_store.uncache_resource('https://api.stormpath.com/v1/accounts/xxx/customData/blah')
        """
        # This modifies any URLs that look like:
        # https://api.stormpath.com/v1/accounts/xxx/customData/key and makes
        # them look like this:
        # https://api.stormpath.com/v1/accounts/xxx/customData
        if 'customData' in href and not href.endswith('customData'):
            parts = href.split('/')
            href = '/'.join(parts[:-1])

        self._get_cache(href).delete(href)

    def get_resource(self, href, params=None):
        """
        This method will retrieve a resource from either the cache, or the
        Stormpath API service.

        If the resource needs to be retrieved from the Stormpath API service, it
        will also be inserted into the cache.

        :param str href: The href of the resource to retrieve.
        :param params: Any additional params to use when fetching the resource.
        :type params: dict or None, optional
        :returns: The retrieved resource.
        :rtype: dict

        Examples::

            account = data_store.get_resource('https://api.stormpath.com/v1/accounts/xxx')
            api_key = data_store.get_resource('https://api.stormpath.com/v1/applications/xxx/apiKeys', params={'id': 'yyy'})
        """

        # TODO:
        #   - encrypt cached api keys
        #   - decrypt cached api keys when retrieving
        #   - check to see if object is cacheable at all (is it a collection?
        #   no)
        #   - recursively cache resources via expansions
        #   - remove expanded resources and 'clean' objects before caching
        data = self._cache_get(href)
        if data is None:
            data = self.executor.get(href, params=params)

            if data.get('items') and len(data['items']) > 0:
                for item in data.get('items'):
                    self._cache_put(item['href'], item)

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

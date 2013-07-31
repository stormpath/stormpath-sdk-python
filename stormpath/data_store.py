from .cache.manager import CacheManager


class DataStore(object):

    CACHE_REGIONS = ('applications', 'directories', 'accounts', 'groups',
        'groupMemberships', 'tenants')

    def __init__(self, executor, cache_options=None):
        self.executor = executor
        self.cache_manager = CacheManager()

        if cache_options is None:
            cache_options = {}

        for region in self.CACHE_REGIONS:
            opts = cache_options.get(region, {})
            if 'store' not in opts and 'store' in cache_options:
                opts['store'] = cache_options['store']
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
        if parts[-2] in self.CACHE_REGIONS:  # we only care about instances
            return self.cache_manager.get_cache(parts[-2]) or NoCache()
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

    def _cache_del(self, href):
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
        self._cache_del(href)

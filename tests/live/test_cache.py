"""Live tests of common cache functionality.
"""

from .base import AuthenticatedLiveBase

from stormpath.client import Client
from stormpath.resources.application import Application
from stormpath.cache.memory_store import MemoryStore
from stormpath.cache.null_cache_store import NullCacheStore


class TestCache(AuthenticatedLiveBase):
    def test_cache_opts_with_different_cache_stores(self):
        cache_opts = {
            'applications': {
                'store': MemoryStore
            },
            'customData': {
                'store': NullCacheStore,
            }
        }

        client = Client(
            id=self.api_key_id, secret=self.api_key_secret,
            scheme=self.AUTH_SCHEME, cache_options=cache_opts)

        app_name = self.get_random_name()
        app = client.applications.create(
            {
                'name': app_name,
                'description': 'test app',
                'custom_data': {'a': 1}
            }
        )
        href = app.href

        # this will cache application
        self.assertEqual(Application(client, href=href).name, app_name)

        # pretend that app name is changed elsewhere
        properties = app._get_properties()
        properties['name'] = 'changed %s' % app_name
        client.data_store.executor.post(app.href, properties)

        # we get stale, cached app name
        self.assertEqual(Application(client, href=href).name, app_name)

        # unless we refresh
        app.refresh()
        self.assertEqual(
            Application(client, href=href).name, properties['name'])

        # this will not cache custom data
        self.assertEqual(Application(client, href=href).custom_data['a'], 1)

        # pretend that app's custom data is changed elsewhere
        properties = app.custom_data._get_properties()
        properties['a'] = 2
        client.data_store.executor.post(app.custom_data.href, properties)

        # we get fresh custom data
        self.assertEqual(Application(client, href=href).custom_data['a'], 2)

        app.delete()

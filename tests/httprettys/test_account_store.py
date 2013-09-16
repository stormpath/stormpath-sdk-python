import unittest
from .test_base import BaseTest
import httpretty
from httpretty import HTTPretty
import json

from stormpath.resource.account_store_mapping import AccountStoreMapping
from stormpath.resource.application import Application
from stormpath.resource.directory import Directory


class TestAccountStore(BaseTest):

    @httpretty.activate
    def test_properties(self):
        httpretty.register_uri(httpretty.GET,
            self.base_href + "/tenants/current",
            location=self.tenant_href,
            status=302)

        httpretty.register_uri(httpretty.GET,
            self.tenant_href,
            body=json.dumps(self.tenant_body),
            content_type="application/json")

        httpretty.register_uri(httpretty.GET,
            self.map_href,
            body=json.dumps(self.map_body),
            content_type="application/json")

        acc_store = self.client.account_store_mappings.get(self.map_href)

        self.assertIsInstance(acc_store, AccountStoreMapping)
        self.assertTrue(acc_store.is_default_account_store)
        self.assertTrue(acc_store.is_default_group_store)
        self.assertEqual(acc_store.list_index, 1)
        self.assertIsInstance(acc_store.application, Application)
        self.assertIsInstance(acc_store.account_store, Directory)

    @httpretty.activate
    def test_delete(self):
        httpretty.register_uri(httpretty.GET,
            self.base_href + "/tenants/current",
            location=self.tenant_href,
            status=302)

        httpretty.register_uri(httpretty.GET,
            self.tenant_href,
            body=json.dumps(self.tenant_body),
            content_type="application/json")

        httpretty.register_uri(httpretty.GET,
            self.map_href,
            body=json.dumps(self.dir_body),
            content_type="application/json")

        httpretty.register_uri(httpretty.DELETE,
            self.map_href,
            body='', status=204)

        acc_store = self.client.account_store_mappings.get(self.map_href)
        acc_store.delete()

        self.assertEqual(HTTPretty.last_request.method, 'DELETE')
        self.assertEqual(HTTPretty.last_request.path, self.map_path)

if __name__ == '__main__':
    unittest.main()

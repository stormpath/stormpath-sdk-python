import unittest
from tests.test_base import BaseTest
import httpretty
import json


class TestTenant(BaseTest):
    @httpretty.activate
    def test_properties(self):

        httpretty.register_uri(httpretty.GET,
            self.base_url + "/tenants/current",
            body=json.dumps(self.tenant_body),
            content_type="application/json")

        self.assertIsNotNone(self.client.tenant.href)
        self.assertIsNotNone(self.client.tenant.name)
        self.assertIsNotNone(self.client.applications)
        self.assertIsNotNone(self.client.directories)

    @httpretty.activate
    def test_get_url(self):

        httpretty.register_uri(httpretty.GET,
            self.base_url + "/tenants/current",
            body=json.dumps(self.tenant_body),
            content_type="application/json")

        httpretty.register_uri(httpretty.GET,
            self.app_href,
            body=json.dumps(self.app_body),
            content_type="application/json")

        application = self.client.applications.get(self.app_href)
        self.assertEqual(application.href, self.app_href)

        httpretty.register_uri(httpretty.GET,
            self.dir_href,
            body=json.dumps(self.dir_body),
            content_type="application/json")

        directory = self.client.directories.get(self.dir_href)
        self.assertEqual(directory.href, self.dir_href)

if __name__ == '__main__':
    unittest.main()

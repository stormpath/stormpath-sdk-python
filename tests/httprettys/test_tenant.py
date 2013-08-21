import unittest
from .test_base import BaseTest
import httpretty
from httpretty import HTTPretty
import json

from stormpath.resource import ResourceList


class TestTenant(BaseTest):
    @httpretty.activate
    def test_properties(self):

        httpretty.register_uri(httpretty.GET,
            self.base_href + "/tenants/current",
            content_type="application/json",
            location=self.tenant_href,
            status=302)

        httpretty.register_uri(httpretty.GET,
            self.tenant_href,
            body=json.dumps(self.tenant_body),
            content_type="application/json")

        self.assertEqual(self.client.tenant.href, "/tenants/current")
        self.assertEqual(self.client.tenant.name, self.tenant_body['name'])
        self.assertEqual(self.client.tenant.key, self.tenant_body['key'])

    @httpretty.activate
    def test_search(self):
        httpretty.register_uri(httpretty.GET,
            self.base_href + "/tenants/current",
            content_type="application/json",
            location=self.tenant_href,
            status=302)

        httpretty.register_uri(httpretty.GET,
            self.tenant_href,
            body=json.dumps(self.tenant_body),
            content_type="application/json")

        # search tenant applications
        self.resource_body = {
            "href": self.tenant_href + "/applications",
            "offset": 0,
            "limit": 25,
            "items": [self.app_body]
        }

        httpretty.register_uri(httpretty.GET,
            self.tenant_href + "/applications",
            body=json.dumps(self.resource_body),
            content_type="application/json")

        applications = self.client.applications.search(self.app_body["name"])
        for app in applications:
            pass

        self.assertIsInstance(applications, ResourceList)
        self.assertEqual(HTTPretty.last_request.method, 'GET')
        self.assertEqual(HTTPretty.last_request.path,
            "%s/applications?q=%s" % (self.tenant_path, self.app_body['name']))

        # search tenant directories
        self.resource_body = {
            "href": self.tenant_href + "/directories",
            "offset": 0,
            "limit": 25,
            "items": [self.dir_body]
        }

        httpretty.register_uri(httpretty.GET,
            self.tenant_href + "/directories",
            body=json.dumps(self.resource_body),
            content_type="application/json")

        directories = self.client.directories.search(self.dir_body['name'])
        for directory in directories:
            pass

        self.assertIsInstance(directories, ResourceList)
        self.assertEqual(HTTPretty.last_request.method, 'GET')
        self.assertEqual(HTTPretty.last_request.path,
            "%s/directories?q=%s" % (self.tenant_path, self.dir_body['name']))

    @httpretty.activate
    def test_associations(self):
        httpretty.register_uri(httpretty.GET,
            self.base_href + "/tenants/current",
            location=self.tenant_href,
            status=302)

        httpretty.register_uri(httpretty.GET,
            self.tenant_href,
            body=json.dumps(self.tenant_body),
            content_type="application/json")

        # applications
        httpretty.register_uri(httpretty.GET,
            self.app_href,
            body=json.dumps(self.app_body),
            content_type="application/json")

        application = self.client.applications.get(self.app_href)
        self.assertEqual(application.href, self.app_href)

        # directories
        httpretty.register_uri(httpretty.GET,
            self.dir_href,
            body=json.dumps(self.dir_body),
            content_type="application/json")

        directory = self.client.directories.get(self.dir_href)
        self.assertEqual(directory.href, self.dir_href)

        # FIXME: accounts and groups are not implemented on server side
        # although it is in rest api docs
        # accounts
        #httpretty.register_uri(httpretty.GET,
            #self.acc_href,
            #body=json.dumps(self.grp_body),
            #content_type="application/json")

        #account = self.client.accounts.get(self.acc_href)
        #self.assertEqual(account.href, self.acc_href)

        # groups
        #httpretty.register_uri(httpretty.GET,
            #self.grp_href,
            #body=json.dumps(self.grp_body),
            #content_type="application/json")

        #group = self.client.groups.get(self.grp_href)
        #self.assertEqual(group.href, self.grp_href)

if __name__ == '__main__':
    unittest.main()

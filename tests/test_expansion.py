import unittest
from tests.test_base import BaseTest
import httpretty
from httpretty import HTTPretty
import json
import re

from stormpath.resource import Expansion


class TestExpansion(BaseTest):

    @httpretty.activate
    def test_pagination(self):
        httpretty.register_uri(httpretty.GET,
            self.base_href + "/tenants/current",
            location=self.tenant_href,
            status=302)

        httpretty.register_uri(httpretty.GET,
            self.tenant_href,
            body=json.dumps(self.tenant_body),
            content_type="application/json")

        httpretty.register_uri(httpretty.GET,
            self.dir_href,
            body=json.dumps(self.dir_body),
            content_type="application/json")

        expansion = Expansion()
        expansion.add_property('groups', limit=10)

        directory = self.client.directories.get(self.dir_href, expansion)
        directory.name

        self.assertTrue(
            self.dir_path + '?expand=groups%28limit%3A10%29'
                == HTTPretty.last_request.path)

    @httpretty.activate
    def test_additional_property(self):
        httpretty.register_uri(httpretty.GET,
            self.base_href + "/tenants/current",
            location=self.tenant_href,
            status=302)

        httpretty.register_uri(httpretty.GET,
            self.tenant_href,
            body=json.dumps(self.tenant_body),
            content_type="application/json")

        httpretty.register_uri(httpretty.GET,
            self.dir_href,
            body=json.dumps(self.dir_body),
            content_type="application/json")

        expansion = Expansion('accounts', 'groups')
        expansion.add_property('applications', offset=0, limit=5)

        directory = self.client.directories.get(self.dir_href, expansion)
        directory.name

        # replace the comma inside parentheses to split easier
        path = re.sub('(applications\%28.*)(\%2C)(.*\%29)',
            '\g<1>;\g<3>', HTTPretty.last_request.path)

        params = path.split('expand=')[1].split('%2C')
        self.assertTrue(
            sorted(params) ==
                sorted(['applications%28offset%3A0;limit%3A5%29', 'accounts', 'groups'])
            or
            sorted(params) ==
                sorted(['applications%28limit%3A5;offset%3A0%29', 'accounts', 'groups'])
        )

if __name__ == '__main__':
    unittest.main()

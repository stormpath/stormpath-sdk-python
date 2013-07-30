import unittest
from tests.test_base import BaseTest
import httpretty
from httpretty import HTTPretty
import json

from stormpath.resource import (AccountList, Directory, GroupMembership)


class TestGroup(BaseTest):

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
            self.dir_href,
            body=json.dumps(self.dir_body),
            content_type="application/json")

        httpretty.register_uri(httpretty.GET,
            self.grp_href,
            body=json.dumps(self.grp_body),
            content_type="application/json")

        directory = self.client.directories.get(self.dir_href)
        group = directory.groups.get(self.grp_href)

        self.assertEqual(group.href, self.grp_href)
        self.assertEqual(group.name, self.grp_body['name'])
        self.assertEqual(group.description, self.grp_body['description'])
        self.assertEqual(group.status, "ENABLED")
        self.assertIsInstance(group.directory, Directory)
        self.assertIsInstance(group.accounts, AccountList)

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
            self.dir_href,
            body=json.dumps(self.dir_body),
            content_type="application/json")

        httpretty.register_uri(httpretty.DELETE,
            self.grp_href,
            body='', status=204)

        httpretty.register_uri(httpretty.GET,
            self.grp_href,
            body=json.dumps(self.grp_body),
            content_type="application/json")

        directory = self.client.directories.get(self.dir_href)
        group = directory.groups.get(self.grp_href)
        group.delete()

        self.assertEqual(HTTPretty.last_request.method, 'DELETE')
        self.assertEqual(HTTPretty.last_request.path,
            self.grp_path)

    @httpretty.activate
    def test_update(self):
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

        httpretty.register_uri(httpretty.GET,
            self.grp_href,
            body=json.dumps(self.grp_body),
            content_type="application/json")

        name = 'Updated Group Name'
        desc = 'Updated Group Desc'
        status = 'DISABLED'

        self.updated_grp_body = {
            "href": self.grp_href,
            "name": name,
            "description": desc,
            "status": status,
            "directory": {
                "href": self.dir_href
            },
            "tenant": {
                "href": self.tenant_href
            },
            "accounts": {
                "href": self.dir_href + "/accounts"
            },
            "groupMemberships": {
                "href": self.grp_href + "/groupMemberships"
            }
        }

        httpretty.register_uri(httpretty.POST,
            self.grp_href,
            body=json.dumps(self.updated_grp_body),
            content_type="application/json")

        directory = self.client.directories.get(self.dir_href)
        group = directory.groups.get(self.grp_href)

        group.name = name
        group.description = desc
        group.status = status
        group.save()

        self.assertEqual(HTTPretty.last_request.method, 'POST')
        self.assertEqual(HTTPretty.last_request.path,
            self.grp_path)

        self.assertEqual(group.name, name)
        self.assertEqual(group.description, desc)
        self.assertEqual(group.status, status)

    @httpretty.activate
    def test_create(self):
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

        httpretty.register_uri(httpretty.POST,
            self.dir_href + "/groups",
            body=json.dumps(self.grp_body),
            status=201,
            content_type="application/json")

        directory = self.client.directories.get(self.dir_href)
        directory.groups.create(self.grp_body)

        self.assertEqual(HTTPretty.last_request.method, 'POST')
        self.assertEqual(HTTPretty.last_request.path, self.dir_path + "/groups")

    @unittest.expectedFailure  # FIXME
    @httpretty.activate
    def test_add_account(self):
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

        httpretty.register_uri(httpretty.GET,
            self.grp_href,
            body=json.dumps(self.grp_body),
            content_type="application/json")

        httpretty.register_uri(httpretty.GET,
            self.acc_href,
            body=json.dumps(self.acc_body),
            content_type="application/json")

        httpretty.register_uri(httpretty.POST,
            self.dir_href + '/groupMemberships',
            body=json.dumps(self.grp_body),
            content_type="application/json")

        directory = self.client.directories.get(self.dir_href)
        group = directory.groups.get(self.grp_href)
        account = directory.accounts.get(self.acc_href)

        grp_mem_href = self.base_href + '/groupMemberships'
        grp_mem_body = {
            "href": "GRP_MEM_HREF",
            "account": {"href": account.href},
            "group": {"href": group.href},
        }
        httpretty.register_uri(httpretty.POST,
            grp_mem_href,
            body=json.dumps(grp_mem_body),
            content_type="application/json")

        group_membership = group.add_account(account)

        self.assertEqual(HTTPretty.last_request.method, 'POST')
        self.assertEqual(HTTPretty.last_request.path, '/v1/groupMemberships')

        self.assertIsInstance(group_membership, GroupMembership)
        self.assertTrue(group_membership.href)
        self.assertEqual(group_membership.account.email, self.acc_body['email'])
        self.assertEqual(group_membership.group.name, self.grp_body['name'])

    # FIXME: groups are not implemented on server side
    # although it is in rest api docs
    # @httpretty.activate
    # def test_search(self):
    #     # fetch group
    #     httpretty.register_uri(httpretty.GET,
    #         self.base_url + "/tenants/current",
    #         body=json.dumps(self.tenant_body),
    #         content_type="application/json")

    #     httpretty.register_uri(httpretty.GET,
    #         self.grp_href,
    #         body=json.dumps(self.grp_body),
    #         content_type="application/json")

    #     group = self.client.groups.get(self.grp_href)

    #     self.resource_body = {
    #         "href": self.grp_href + "/accounts",
    #         "offset": 0,
    #         "limit": 25,
    #         "items": [self.acc_href]
    #     }

    #     # search group accounts without attributes
    #     httpretty.register_uri(httpretty.GET,
    #         self.grp_href + "/accounts",
    #         body=json.dumps(self.resource_body),
    #         content_type="application/json")

    #     accounts = group.accounts.search("ACC_USERNAME")
    #     for acc in accounts:
    #         pass

    #     self.assertIsInstance(accounts, AccountResourceList)
    #     self.assertEqual(HTTPretty.last_request.method, 'GET')
    #     self.assertEqual(HTTPretty.last_request.path,
    #         "%s/accounts?q=%s" % (self.app_path,
    #                                     self.acc_body['username']))

    #     # search group accounts with attributes
    #     httpretty.register_uri(httpretty.GET,
    #         self.grp_href + "/accounts?givenName=ACC_USERNAME",
    #         body=json.dumps(self.resource_body),
    #         content_type="application/json")

    #     accounts = group.accounts.search({
    #        "given_name": "ACC_USERNAME"})
    #     for acc in accounts:
    #         pass

    #     self.assertIsInstance(accounts, AccountResourceList)
    #     self.assertEqual(HTTPretty.last_request.method, 'GET')
    #     self.assertEqual(HTTPretty.last_request.path,
    #        "%s/accounts?givenName=%s" % (self.grp_path,
    #                                    self.acc_body['username']))

    @unittest.expectedFailure  # FIXME
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

        httpretty.register_uri(httpretty.GET,
            self.dir_href,
            body=json.dumps(self.dir_body),
            content_type="application/json")

        directory = self.client.directories.get(self.dir_href)

        httpretty.register_uri(httpretty.GET,
            self.grp_href,
            body=json.dumps(self.grp_body),
            content_type="application/json")

        group = directory.groups.get(self.grp_href)

        # accounts
        httpretty.register_uri(httpretty.GET,
            self.acc_href,
            body=json.dumps(self.acc_body),
            content_type="application/json")

        account = group.accounts.get(self.acc_href)
        self.assertEqual(account.href, self.acc_href)

        # directory
        self.assertEqual(group.directory.href, self.dir_href)

        # tenant
        httpretty.register_uri(httpretty.GET,
            self.tenant_href,
            body=json.dumps(self.tenant_body),
            content_type="application/json")

        # tenant
        self.assertEqual(group.tenant.name, self.tenant_body['name'])


if __name__ == '__main__':
    unittest.main()

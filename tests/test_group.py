import unittest
from tests.test_base import BaseTest
import httpretty
from httpretty import HTTPretty
import json
import re

from stormpath.resource import (AccountResourceList, Tenant, Directory,
    GroupMembership)


class TestGroup(BaseTest):

    @httpretty.activate
    def test_properties(self):
        httpretty.register_uri(httpretty.GET,
            self.base_url + "/tenants/current",
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

        name = 'GRP_NAME'
        desc = 'GRP_DESC'
        dir_name = 'DIR_NAME'

        directory = self.client.directories.get(self.dir_href)
        group = directory.groups.get(self.grp_href)

        self.assertEqual(group.name, name)
        self.assertEqual(group.description, desc)
        self.assertEqual(group.status, "enabled")
        self.assertEqual(group.directory.name, dir_name)
        self.assertIsInstance(group.directory, Directory)
        self.assertIsInstance(group.accounts, AccountResourceList)
        self.assertIsInstance(group.tenant, Tenant)

    @httpretty.activate
    def test_delete(self):

        httpretty.register_uri(httpretty.GET,
            self.base_url + "/tenants/current",
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
            body=json.dumps(self.acc_body),
            content_type="application/json")

        directory = self.client.directories.get(self.dir_href)
        group = directory.accounts.get(self.grp_href)
        group.delete()

        self.assertEqual(HTTPretty.last_request.method, 'DELETE')
        self.assertEqual(HTTPretty.last_request.path,
            '/v1/groups/GRP_HREF')

    @httpretty.activate
    def test_update(self):
        httpretty.register_uri(httpretty.GET,
            self.base_url + "/tenants/current",
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
        status = 'disabled'

        self.updated_grp_body = {
            "href": self.grp_href,
            "name": name,
            "description": desc,
            "status": status,
            "directory": {
                "href": self.dir_href
                },
            "tenant": {
                "href": self.base_url + "/tenants/TENANT_ID"
                },
            "accounts": {
                "href": self.dir_href + "/accounts"
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

        self.assertEqual(group.name, name)
        self.assertEqual(group.description, desc)
        self.assertEqual(group.status, status)
        self.assertEqual(group.status, "disabled")

        self.assertEqual(HTTPretty.last_request.method, 'POST')
        self.assertEqual(HTTPretty.last_request.path, '/v1/groups/GRP_HREF')

    @httpretty.activate
    def test_add_account(self):
        httpretty.register_uri(httpretty.GET,
            self.base_url + "/tenants/current",
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

        httpretty.register_uri(httpretty.POST,
            self.dir_href + '/accounts',
            body=json.dumps(self.acc_body),
            content_type="application/json")

        httpretty.register_uri(httpretty.POST,
            self.dir_href + '/groupMemberships',
            body=json.dumps(self.grp_body),
            content_type="application/json")

        directory = self.client.directories.get(self.dir_href)
        group = directory.groups.get(self.grp_href)

        email = 'ACC_EMAIL'
        acc_props = {
            "email": email,
            "givenName": "Given Name",
            "surname": "Surname",
            "password": "superP4ss"
        }

        account = group.directory.create_account(acc_props)

        grp_mem_href = self.base_url + '/groupMemberships'
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

        self.assertIsInstance(group_membership, GroupMembership)
        self.assertTrue(group_membership.href)
        self.assertEqual(group_membership.account.email, email)
        self.assertEqual(group_membership.group.name, 'GRP_NAME')

        self.assertEqual(HTTPretty.last_request.method, 'POST')
        self.assertEqual(HTTPretty.last_request.path, '/v1/groupMemberships')

    # PENDING FURTHER INVESTIGATION
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

    #     regex = '\/v1\/groups\/GRP_HREF\/accounts\?' \
    #         + '.*((?=.*offset=0)(?=.*limit=25)(?=.*q=ACC_USERNAME).*$)'
    #     self.assertIsInstance(accounts, AccountResourceList)
    #     self.assertEqual(HTTPretty.last_request.method, 'GET')
    #     self.assertIsNotNone(re.search(regex, HTTPretty.last_request.path))

    #     # search group accounts with attributes
    #     httpretty.register_uri(httpretty.GET,
    #         self.grp_href + "/accounts?givenName=ACC_USERNAME",
    #         body=json.dumps(self.resource_body),
    #         content_type="application/json")

    #     accounts = group.accounts.search(givenName="ACC_USERNAME")
    #     for acc in accounts:
    #         pass

    #     regex = '\/v1\/groups\/GRP_HREF\/accounts\?' \
    #         + '.*((?=.*offset=0)(?=.*limit=25)(?=.*givenName=ACC_USERNAME).*$)'
    #     self.assertIsInstance(accounts, AccountResourceList)
    #     self.assertEqual(HTTPretty.last_request.method, 'GET')
    #     self.assertIsNotNone(re.search(regex, HTTPretty.last_request.path))

if __name__ == '__main__':
    unittest.main()

import unittest
from tests.test_base import BaseTest
import httpretty
from httpretty import HTTPretty
import json
import re

from stormpath.resource import (AccountResourceList, GroupResourceList,
    Tenant, Account, Group)


class TestDirectory(BaseTest):
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

        directory = self.client.directories.get(self.dir_href)

        self.assertEqual(directory.name, "DIR_NAME")
        self.assertEqual(directory.description, "DIR_DESC")
        self.assertEqual(directory.status, "enabled")

        self.assertEqual(HTTPretty.last_request.path, '/v1/directories/DIR_HREF')

        self.assertIsInstance(directory.accounts, AccountResourceList)
        self.assertIsInstance(directory.groups, GroupResourceList)
        self.assertIsInstance(directory.tenant, Tenant)

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
            self.dir_href,
            body='', status=204)

        directory = self.client.directories.get(self.dir_href)
        directory.delete()

        self.assertEqual(HTTPretty.last_request.method, 'DELETE')
        self.assertEqual(HTTPretty.last_request.path,
            '/v1/directories/DIR_HREF')

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

        dir_name, dir_desc = "Updated Dir Name", "Updated Dir Desc"
        status = "disabled"

        self.dir_updated_body = {
            "href": self.dir_href,
            "name": dir_name, "description": dir_desc,
            "status": status,
            "tenant": {
                "href": self.base_url + "/tenants/TENANT_ID"
                },
            "accounts": {
                "href": self.dir_href + "/accounts"
                },
            "groups": {
                "href": self.dir_href + "/groups"
                }
            }

        httpretty.register_uri(httpretty.POST,
            self.dir_href,
            body=json.dumps(self.dir_updated_body),
            content_type="application/json")

        directory = self.client.directories.get(self.dir_href)

        directory.name = dir_name
        directory.description = dir_desc
        directory.status = status
        directory.save()

        self.assertEqual(directory.name, dir_name)
        self.assertEqual(directory.description, dir_desc)
        self.assertEqual(directory.status, status)

        self.assertEqual(HTTPretty.last_request.method, 'POST')
        self.assertEqual(HTTPretty.last_request.path, '/v1/directories/DIR_HREF')

    @httpretty.activate
    def test_create(self):
        httpretty.register_uri(httpretty.GET,
            self.base_url + "/tenants/current",
            body=json.dumps(self.tenant_body),
            content_type="application/json")

        httpretty.register_uri(httpretty.POST,
            self.base_url + "/directories",
            body=json.dumps(self.dir_body),
            content_type="application/json")

        dir_name = "DIR_NAME"
        dir_desc = "DIR_DESC"
        status = "enabled"

        directory = self.client.directories.create({
            "name": dir_name,
            "description": dir_desc,
            "enabled": status
        })

        self.assertEqual(HTTPretty.last_request.method, 'POST')
        self.assertEqual(HTTPretty.last_request.path, '/v1/directories')

        self.assertEqual(directory.name, dir_name)
        self.assertEqual(directory.description, dir_desc)
        self.assertEqual(directory.status, status)

    @httpretty.activate
    def test_create_account(self):
        httpretty.register_uri(httpretty.GET,
            self.base_url + "/tenants/current",
            body=json.dumps(self.tenant_body),
            content_type="application/json")

        httpretty.register_uri(httpretty.GET,
            self.dir_href,
            body=json.dumps(self.dir_body),
            content_type="application/json")

        directory = self.client.directories.get(self.dir_href)

        email = "newuser@superenterprise.comy"
        account_dict = {
            "username": "superuser123",
            "email": email,
            "givenName": "Super",
            "surname": "User",
            "password": "uGhd%a8Kl!"
        }

        body = {
            "href": self.acc_href,
            "username": "superuser123",
            "email": email,
            "fullName": "Super User",
            "givenName": "Super",
            "middleName": None,
            "surname": "User",
            "status": "enabled",
            "groups": {
                "href": self.acc_href + "/groups"
                },
            "groupMemberships": {
                "href": self.acc_href + "groupMemfaberships"
                },
                "directory": {
                    "href": self.dir_href
                    },
                    "tenant": {
                        "href": self.base_url + "/tenants/TENANT_ID"
                        },
                    "emailVerificationToken": None
                }

        httpretty.register_uri(httpretty.POST,
            self.dir_href + '/accounts',
            body=json.dumps(body),
            content_type="application/json")

        account = directory.create_account(account_dict)

        self.assertEqual(HTTPretty.last_request.method, 'POST')
        self.assertEqual(HTTPretty.last_request.path,
            '/v1/directories/DIR_HREF/accounts')

        self.assertIsInstance(account, Account)
        self.assertEqual(account.email, email)
        self.assertTrue(account.href)

    @httpretty.activate
    def test_create_group(self):
        httpretty.register_uri(httpretty.GET,
            self.base_url + "/tenants/current",
            body=json.dumps(self.tenant_body),
            content_type="application/json")

        httpretty.register_uri(httpretty.GET,
            self.dir_href,
            body=json.dumps(self.dir_body),
            content_type="application/json")

        directory = self.client.directories.get(self.dir_href)

        httpretty.register_uri(httpretty.POST,
            self.dir_href + '/groups',
            body=json.dumps(self.grp_body),
            content_type="application/json")

        name = "GRP_NAME"
        group = directory.create_group({"name": name})

        self.assertEqual(HTTPretty.last_request.method, 'POST')
        self.assertEqual(HTTPretty.last_request.path,
            '/v1/directories/DIR_HREF/groups')

        self.assertIsInstance(group, Group)
        self.assertEqual(group.name, name)
        self.assertTrue(group.href)

    @httpretty.activate
    def test_search(self):
        # fetch directory
        httpretty.register_uri(httpretty.GET,
            self.base_url + "/tenants/current",
            body=json.dumps(self.tenant_body),
            content_type="application/json")

        httpretty.register_uri(httpretty.GET,
            self.dir_href,
            body=json.dumps(self.dir_body),
            content_type="application/json")

        directory = self.client.directories.get(self.dir_href)

        self.resource_body = {
            "href": self.dir_href + "/accounts",
            "offset": 0,
            "limit": 25,
            "items": [self.acc_body]
        }

        httpretty.register_uri(httpretty.GET,
            self.dir_href + "/groups",
            body=json.dumps(self.resource_body),
            content_type="application/json")

        # search directory accounts without attributes
        httpretty.register_uri(httpretty.GET,
            self.dir_href + "/accounts",
            body=json.dumps(self.resource_body),
            content_type="application/json")

        accounts = directory.accounts.search("ACC_USERNAME")
        for acc in accounts:
            pass

        regex = '\/v1\/directories\/DIR_HREF\/accounts\?' \
            + '.*((?=.*offset=0)(?=.*limit=25)(?=.*q=ACC_USERNAME).*$)'
        self.assertIsInstance(accounts, AccountResourceList)
        self.assertEqual(HTTPretty.last_request.method, 'GET')
        self.assertIsNotNone(re.search(regex, HTTPretty.last_request.path))

        # search directory accounts with attributes
        accounts = directory.accounts.search(givenName="ACC_USERNAME")
        for acc in accounts:
            pass

        regex = '\/v1\/directories\/DIR_HREF\/accounts\?' \
            + '.*((?=.*offset=0)(?=.*limit=25)(?=.*givenName=ACC_USERNAME).*$)'
        self.assertIsInstance(accounts, AccountResourceList)
        self.assertEqual(HTTPretty.last_request.method, 'GET')
        self.assertIsNotNone(re.search(regex, HTTPretty.last_request.path))

        # search directory groups without attributes
        self.resource_body = {
            "href": self.dir_href + "/groups",
            "offset": 0,
            "limit": 25,
            "items": [self.grp_body]
        }

        httpretty.register_uri(httpretty.GET,
            self.dir_href + "/groups",
            body=json.dumps(self.resource_body),
            content_type="application/json")

        groups = directory.groups.search("GRP_NAME")
        for group in groups:
            pass

        regex = '\/v1\/directories\/DIR_HREF\/groups\?' \
            + '.*((?=.*offset=0)(?=.*limit=25)(?=.*q=GRP_NAME).*$)'
        self.assertIsInstance(groups, GroupResourceList)
        self.assertEqual(HTTPretty.last_request.method, 'GET')
        self.assertIsNotNone(re.search(regex, HTTPretty.last_request.path))

        # search directory groups with attributes
        groups = directory.groups.search(name="GRP_NAME")
        for group in groups:
            pass

        regex = '\/v1\/directories\/DIR_HREF\/groups\?' \
            + '.*((?=.*offset=0)(?=.*limit=25)(?=.*name=GRP_NAME).*$)'
        self.assertIsInstance(groups, GroupResourceList)
        self.assertEqual(HTTPretty.last_request.method, 'GET')
        self.assertIsNotNone(re.search(regex, HTTPretty.last_request.path))


if __name__ == '__main__':
    unittest.main()

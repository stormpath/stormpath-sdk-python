import unittest
from tests.test_base import BaseTest
import httpretty
from httpretty import HTTPretty
import json
import re

from stormpath.resource import (AccountList, GroupList, Account, Group)


class TestDirectory(BaseTest):
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

        directory = self.client.directories.get(self.dir_href)

        self.assertEqual(directory.href, self.dir_body['href'])
        self.assertEqual(directory.name, self.dir_body['name'])
        self.assertEqual(directory.description, self.dir_body['description'])
        self.assertEqual(directory.status, self.dir_body['status'])

        self.assertEqual(HTTPretty.last_request.path, self.dir_path)

        self.assertIsInstance(directory.accounts, AccountList)
        self.assertIsInstance(directory.groups, GroupList)

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
            self.dir_href,
            body='', status=204)

        directory = self.client.directories.get(self.dir_href)
        directory.delete()

        self.assertEqual(HTTPretty.last_request.method, 'DELETE')
        self.assertEqual(HTTPretty.last_request.path, self.dir_path)

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
        self.assertEqual(HTTPretty.last_request.path, self.dir_path)

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

        httpretty.register_uri(httpretty.POST,
            self.base_href + "/directories",
            body=json.dumps(self.dir_body),
            content_type="application/json")

        directory = self.client.directories.create({
            "name": self.dir_body['name'],
            "description": self.dir_body['description'],
            "enabled": self.dir_body['status']
        })

        self.assertEqual(HTTPretty.last_request.method, 'POST')
        self.assertEqual(HTTPretty.last_request.path, '/v1/directories')

        self.assertEqual(directory.name, self.dir_body['name'])
        self.assertEqual(directory.description, self.dir_body['description'])
        self.assertEqual(directory.status, self.dir_body['status'])

    @httpretty.activate
    def test_create_account(self):
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

        username = "superuser123"
        email = "newuser@superenterprise.comy"
        given_name = "Super"
        surname = "User"
        password = "uGhd%a8Kl!"

        new_user_body = {
            "href": self.acc_href,
            "username": username,
            "email": email,
            "fullName": "%s %s" % (given_name, surname),
            "givenName": given_name,
            "middleName": None,
            "surname": surname,
            "status": "DISABLED",
            "groups": {
                "href": self.acc_href + "/groups"
                },
            "groupMemberships": {
                "href": self.acc_href + "/groupMemberships"
                },
                "directory": {
                    "href": self.dir_href
                    },
                    "tenant": {
                        "href": self.tenant_href
                        },
                    "emailVerificationToken": None
                }

        httpretty.register_uri(httpretty.POST,
            self.dir_href + '/accounts',
            body=json.dumps(new_user_body),
            content_type="application/json")

        account_dict = {
            "username": username,
            "email": email,
            "givenName": given_name,
            "surname": surname,
            "password": password
        }

        account = directory.create_account(account_dict)
        self.assertEqual(HTTPretty.last_request.method, 'POST')
        self.assertEqual(HTTPretty.last_request.path,
            self.dir_path + '/accounts')

        self.assertIsInstance(account, Account)
        self.assertEqual(account.email, email)
        self.assertTrue(account.href)

        new_user_body = {
            "href": self.acc_href,
            "username": username,
            "email": email,
            "fullName": "%s %s" % (given_name, surname),
            "givenName": given_name,
            "middleName": None,
            "surname": surname,
            "status": "DISABLED",
            "groups": {
                "href": self.acc_href + "/groups"
                },
            "groupMemberships": {
                "href": self.acc_href + "/groupMemberships"
                },
                "directory": {
                    "href": self.dir_href
                    },
                    "tenant": {
                        "href": self.tenant_href
                        },
                    "emailVerificationToken": {
                        "href": self.base_href +
                            "/accounts/emailVerificationToken/TOKEN"
                    }
                }

        httpretty.register_uri(httpretty.POST,
            self.dir_href + '/accounts',
            body=json.dumps(new_user_body),
            content_type="application/json")

        account = directory.create_account(account_dict, False)

        self.assertEqual(HTTPretty.last_request.method, 'POST')
        self.assertEqual(HTTPretty.last_request.path,
            self.dir_path + '/accounts?registrationWorkflowEnabled=false')

        self.assertIsInstance(account, Account)
        self.assertEqual(account.email, email)
        self.assertTrue(account.href)

    @httpretty.activate
    def test_create_group(self):
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

        httpretty.register_uri(httpretty.POST,
            self.dir_href + '/groups',
            body=json.dumps(self.grp_body),
            content_type="application/json")

        name = "GRP_NAME"
        group = directory.groups.create({"name": name})

        self.assertEqual(HTTPretty.last_request.method, 'POST')
        self.assertEqual(HTTPretty.last_request.path,
            self.dir_path + '/groups')

        self.assertIsInstance(group, Group)
        self.assertEqual(group.name, name)
        self.assertTrue(group.href)

    @httpretty.activate
    def test_search(self):
        # fetch directory
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

        accounts = directory.accounts.search(self.acc_body['username'])
        for acc in accounts:
            pass

        self.assertIsInstance(accounts, AccountList)
        self.assertEqual(HTTPretty.last_request.method, 'GET')
        self.assertEqual(HTTPretty.last_request.path,
            "%s/accounts?q=%s" % (self.dir_path, self.acc_body['username']))

        # search directory accounts with attributes
        accounts = directory.accounts.search({
            'givenName': self.acc_body['username']})
        for acc in accounts:
            pass

        self.assertIsInstance(accounts, AccountList)
        self.assertEqual(HTTPretty.last_request.method, 'GET')
        self.assertEqual(HTTPretty.last_request.path,
            "%s/accounts?givenName=%s" % (self.dir_path,
                self.acc_body['username']))

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

        groups = directory.groups.search(self.grp_body['name'])
        for group in groups:
            pass

        self.assertIsInstance(groups, GroupList)
        self.assertEqual(HTTPretty.last_request.method, 'GET')
        self.assertEqual(HTTPretty.last_request.path,
            "%s/groups?q=%s" % (self.dir_path, self.grp_body['name']))

        # search directory groups with attributes
        groups = directory.groups.search({
            'name': 'GRP_NAME'})
        for group in groups:
            pass

        self.assertIsInstance(groups, GroupList)
        self.assertEqual(HTTPretty.last_request.method, 'GET')
        self.assertEqual(HTTPretty.last_request.path,
            "%s/groups?name=%s" % (self.dir_path, self.grp_body['name']))

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

        # accounts
        httpretty.register_uri(httpretty.GET,
            self.acc_href,
            body=json.dumps(self.acc_body),
            content_type="application/json")

        account = directory.accounts.get(self.acc_href)
        self.assertEqual(account.href, self.acc_href)

        # groups
        httpretty.register_uri(httpretty.GET,
            self.grp_href,
            body=json.dumps(self.grp_body),
            content_type="application/json")

        group = directory.groups.get(self.grp_href)
        self.assertEqual(group.href, self.grp_href)

        # tenant
        self.assertEqual(directory.tenant.name, self.tenant_body['name'])

if __name__ == '__main__':
    unittest.main()

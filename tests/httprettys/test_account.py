# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import unittest
from .test_base import BaseTest
import httpretty
from httpretty import HTTPretty
import json

from stormpath.resource import (Directory, GroupList,
    GroupMembership, GroupMembershipList, Resource, Expansion)
from stormpath.error import Error


class TestAccount(BaseTest):

    @httpretty.activate
    def test_properties(self):

        username = 'ACC_USERNAME'
        email = 'ACC_EMAIL'
        given_name = 'ACC_GIVENNAME'
        surname = 'ACC_SURNAME'
        dir_name = 'DIR_NAME'

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
            self.acc_href,
            body=json.dumps(self.acc_body),
            content_type="application/json")

        httpretty.register_uri(
            httpretty.POST,
            self.custom_href,
            body=json.dumps(self.custom_body),
            content_type="application/json")

        account = self.client.accounts.get(self.acc_href)

        self.assertEqual(account.username, username)
        self.assertEqual(account.email, email)
        self.assertEqual(account.given_name, given_name)
        self.assertEqual(str(account), username)

        self.assertEqual(HTTPretty.last_request.path, self.acc_path)

        self.assertEqual(account.surname, surname)
        self.assertEqual(account.directory.name, dir_name)
        self.assertIsInstance(account.directory, Directory)
        self.assertIsInstance(account.groups, GroupList)
        self.assertIsInstance(account.group_memberships,
            GroupMembershipList)

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
            self.acc_href,
            body='', status=204)

        httpretty.register_uri(httpretty.GET,
            self.acc_href,
            body=json.dumps(self.acc_body),
            content_type="application/json")

        directory = self.client.directories.get(self.dir_href)
        account = directory.accounts.get(self.acc_href)
        account.delete()

        self.assertEqual(HTTPretty.last_request.method, 'DELETE')
        self.assertEqual(HTTPretty.last_request.path, self.acc_path)

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

        httpretty.register_uri(
            httpretty.POST,
            self.custom_href,
            body=json.dumps(self.custom_body),
            content_type="application/json")

        body = {
            "href": self.acc_href,
            "username": "superuser123",
            "email": "superuser123@superemail.comy",
            "fullName": "Super User",
            "givenName": "Super",
            "middleName": None,
            "surname": "User",
            "status": "enabled",
            "customData": {"href": self.custom_href},
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
                        "href": self.base_href + "/tenants/TENANT_ID"
                        },
                    "emailVerificationToken": None
                }

        httpretty.register_uri(httpretty.GET,
            self.acc_href,
            body=json.dumps(body),
            content_type="application/json")

        directory = self.client.directories.get(self.dir_href)
        account = directory.accounts.get(self.acc_href)

        body = {
            "href": self.acc_href,
            "username": "superuser123changedUser Changed",
            "email": "superuser123changed@superemail.comy",
            "fullName": "Super Changed middle User Changed",
            "givenName": "Super Changed",
            "middleName": "middle",
            "surname": "User Changed",
            "status": "disabled",
            "customData": {"href": self.custom_href},
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
            self.acc_href,
            body=json.dumps(body),
            content_type="application/json")

        username = 'superuser123changed'
        email = 'superuser123changed@superemail.comy'
        given_name = 'Super Changed'
        surname = 'User Changed'
        password = 'superP4ssChanged'
        status = 'disabled'

        account.username = username
        account.email = email
        account.given_name = given_name
        account.surname = surname
        account.password = password
        account.middle_name = 'middle'
        account.status = status

        account.save()

        self.assertEqual(HTTPretty.last_request.method, 'POST')
        self.assertEqual(HTTPretty.last_request.path, self.acc_path)

        self.assertEqual(account.username, username)
        self.assertEqual(account.email, email)
        self.assertEqual(account.given_name, given_name)
        self.assertEqual(account.surname, surname)
        self.assertEqual(account.middle_name, 'middle')
        self.assertEqual(account.status, status)

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

        body = {
            "href": self.acc_href,
            "username": "superuser123",
            "email": "superuser123@superemail.comy",
            "fullName": "Super User",
            "givenName": "Super",
            "middleName": None,
            "surname": "User",
            "status": "enabled",
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
            self.dir_href + "/accounts",
            body=json.dumps(body),
            content_type="application/json")

        username, email = 'superuser123', 'superuser123@superemail.comy'
        given_name, surname, dir_name = 'Super', 'User', 'New Dir Name 123 Ha!'
        password = 'superP4ss'

        account_dict = {
            'username': username,
            'email': email,
            'given_name': given_name,
            'surname': surname,
            'password': password
        }

        directory = self.client.directories.get(self.dir_href)
        account = directory.accounts.create(account_dict)

        self.assertEqual(HTTPretty.last_request.method, 'POST')
        self.assertEqual(HTTPretty.last_request.path,
            self.dir_path + '/accounts')

        self.assertEqual(account.username, username)
        self.assertEqual(account.email, email)
        self.assertEqual(account.given_name, given_name)
        self.assertEqual(account.surname, surname)
        self.assertIsInstance(account.email_verification_token, Resource)

    @httpretty.activate
    def test_verify_email(self):
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

        new_user_body = {
            "href": self.acc_href,
            "username": "USERNAME",
            "email": "EMAIL",
            "fullName": "Full Name",
            "givenName": "GNAME",
            "middleName": None,
            "surname": "SURNAME",
            "status": "UNVERIFIED",
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
                    "/accounts/emailVerificationTokens/TOKEN"
                }
            }

        httpretty.register_uri(httpretty.POST,
            self.dir_href + "/accounts",
            body=json.dumps(new_user_body),
            content_type="application/json")

        account_dict = {
            'username': "USERNAME",
            'email': "EMAIL",
            'givenName': "GNAME",
            'surname': "SURNAME",
            'password': "PASSWORD"
        }

        account = directory.accounts.create(account_dict)

        self.assertIsInstance(account.email_verification_token, Resource)

        verification_body = {'href': self.acc_href}
        httpretty.register_uri(httpretty.POST,
            self.base_href + "/accounts/emailVerificationTokens/TOKEN",
            body=json.dumps(verification_body),
            content_type="application/json")

        self.assertEqual(account.status, 'UNVERIFIED')
        account2 = directory.accounts.verify_email_token('TOKEN')
        self.assertEqual(account.href, account2.href)
        self.assertEqual(HTTPretty.last_request.method, 'POST')
        self.assertEqual(HTTPretty.last_request.path,
            self.base_path + "/accounts/emailVerificationTokens/TOKEN")

        httpretty.register_uri(httpretty.GET,
            self.acc_href,
            body=json.dumps(new_user_body),
            content_type="application/json")

        self.assertEqual(account.username, "USERNAME")
        self.assertEqual(account.email, "EMAIL")
        self.assertEqual(account.given_name, "GNAME")

        invalid_token = {
            "code": 404,
            "developerMessage": "The requested resource does not exist.",
            "message": "The requested resource does not exist.",
            "moreInfo": "mailto:support@stormpath.com",
            "status": 404
        }

        httpretty.register_uri(httpretty.POST,
            self.base_href + "/accounts/emailVerificationTokens/TOKEN",
            body=json.dumps(invalid_token),
            status=404)

        with self.assertRaises(Error):
            directory.accounts.verify_email_token('TOKEN')

    @httpretty.activate
    def test_authenticate(self):
        httpretty.register_uri(httpretty.GET,
            self.base_href + "/tenants/current",
            location=self.tenant_href,
            status=302)

        httpretty.register_uri(httpretty.GET,
            self.tenant_href,
            body=json.dumps(self.tenant_body),
            content_type="application/json")

        httpretty.register_uri(httpretty.GET,
            self.app_href,
            body=json.dumps(self.app_body),
            content_type="application/json")

        body = {
            "account": {
                "href": self.acc_href
            }
        }

        httpretty.register_uri(httpretty.POST,
            self.app_href + "/loginAttempts",
            body=json.dumps(body),
            content_type="application/json")

        httpretty.register_uri(httpretty.GET,
            self.acc_href,
            body=json.dumps(body),
            content_type="application/json")

        application = self.client.applications.get(self.app_href)
        account = application.authenticate_account("USERNAME", "PAŠVORD")

        self.assertEqual(HTTPretty.last_request.method, "POST")
        self.assertEqual(HTTPretty.last_request.path,
            "%s/%s" % (self.app_path, "loginAttempts"))

        self.assertEqual(application.href, self.app_href)
        self.assertEqual(account.href, self.acc_href)

        expansion = Expansion('account')
        account = application.authenticate_account("USERNAME", "PAŠVORD",
            expand=expansion)

        self.assertEqual(HTTPretty.last_request.method, "POST")
        self.assertEqual(HTTPretty.last_request.path,
            "%s/%s?expand=account" % (self.app_path, "loginAttempts"))

    @httpretty.activate
    def test_add_group(self):
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
            self.dir_href + '/groups',
            body=json.dumps(self.grp_body),
            content_type="application/json")

        httpretty.register_uri(httpretty.GET,
            self.acc_href,
            body=json.dumps(self.acc_body),
            content_type="application/json")

        httpretty.register_uri(httpretty.GET,
            self.grp_href,
            body=json.dumps(self.grp_body),
            content_type="application/json")

        account = self.client.accounts.get(self.acc_href)

        group_name = 'GRP_NAME'
        group = account.directory.groups.create({"name": group_name})

        self.assertEqual(HTTPretty.last_request.method, 'POST')
        self.assertEqual(HTTPretty.last_request.path,
            self.dir_path + '/groups')

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

        group_membership = account.add_group(group)

        self.assertEqual(HTTPretty.last_request.method, 'POST')
        self.assertEqual(HTTPretty.last_request.path, '/v1/groupMemberships')

        self.assertIsInstance(group_membership, GroupMembership)
        self.assertTrue(group_membership.href)
        self.assertEqual(group_membership.group.name, group_name)

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

        httpretty.register_uri(httpretty.GET,
            self.acc_href,
            body=json.dumps(self.acc_body),
            content_type="application/json")

        account = self.client.accounts.get(self.acc_href)

        # groups
        httpretty.register_uri(httpretty.GET,
            self.grp_href,
            body=json.dumps(self.grp_body),
            content_type="application/json")

        group = account.groups.get(self.grp_href)
        self.assertEqual(group.href, self.grp_href)

        # directory
        self.assertEqual(account.directory.href, self.dir_href)

if __name__ == '__main__':
    unittest.main()

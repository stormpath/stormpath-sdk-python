import unittest
from tests.test_base import BaseTest
import httpretty
from httpretty import HTTPretty
import json
import re

from stormpath.resource import (Tenant, Account, AccountResourceList,
    GroupResourceList)


class TestApplication(BaseTest):

    @httpretty.activate
    def test_properties(self):

        httpretty.register_uri(httpretty.GET,
            self.base_href + "/tenants/current",
            body=json.dumps(self.tenant_body),
            content_type="application/json")

        httpretty.register_uri(httpretty.GET,
            self.app_href,
            body=json.dumps(self.app_body),
            content_type="application/json")

        app_name, app_desc = "APP_NAME", "APP_DESC"
        application = self.client.applications.get(self.app_href)

        self.assertEqual(application.name, self.app_body['name'])
        self.assertEqual(application.description, self.app_body['description'])
        self.assertEqual(application.status, self.app_body['status'])
        self.assertEqual(HTTPretty.last_request.path, self.app_path)

        self.assertIsInstance(application.accounts, AccountResourceList)
        self.assertIsInstance(application.tenant, Tenant)

    @httpretty.activate
    def test_delete(self):

        httpretty.register_uri(httpretty.GET,
            self.base_href + "/tenants/current",
            body=json.dumps(self.tenant_body),
            content_type="application/json")

        httpretty.register_uri(httpretty.GET,
            self.app_href,
            body=json.dumps(self.app_body),
            content_type="application/json")

        httpretty.register_uri(httpretty.DELETE,
            self.app_href,
            body='', status=204)

        application = self.client.applications.get(self.app_href)
        application.delete()

        self.assertEqual(HTTPretty.last_request.method, 'DELETE')
        self.assertEqual(HTTPretty.last_request.path, self.app_path)

    @httpretty.activate
    def test_update(self):

        httpretty.register_uri(httpretty.GET,
            self.base_href + "/tenants/current",
            body=json.dumps(self.tenant_body),
            content_type="application/json")

        httpretty.register_uri(httpretty.GET,
            self.app_href,
            body=json.dumps(self.app_body),
            content_type="application/json")

        app_name, app_desc = "Updated App Name", "Updated App Desc"
        status = "disabled"

        self.app_updated_body = {
            "href": self.app_href,
            "name": app_name, "description": app_desc,
            "status": status,
            "tenant": {
                "href": self.base_url + "/tenants/TENANT_ID"
                },
            "accounts": {
                "href": self.app_href + "/accounts"
                },
            "groups": {
                "href": self.app_href + "/groups"
                },
            "passwordResetTokens": {
                "href": self.app_href + "/passwordResetTokens"
                }
            }

        httpretty.register_uri(httpretty.POST,
            self.app_href,
            body=json.dumps(self.app_updated_body),
            content_type="application/json")

        application = self.client.applications.get(self.app_href)

        application.name = app_name
        application.description = app_desc
        application.status = status
        application.save()

        self.assertEqual(application.name, app_name)
        self.assertEqual(application.description, app_desc)
        self.assertEqual(application.status, status)

        self.assertEqual(HTTPretty.last_request.method, 'POST')
        self.assertEqual(HTTPretty.last_request.path, self.app_path)

    @httpretty.activate
    def test_send_password_reset_email(self):

        httpretty.register_uri(httpretty.GET,
            self.base_href + "/tenants/current",
            body=json.dumps(self.tenant_body),
            content_type="application/json")

        httpretty.register_uri(httpretty.GET,
            self.app_href,
            body=json.dumps(self.app_body),
            content_type="application/json")

        httpretty.register_uri(httpretty.POST,
            "%s/passwordResetTokens" % self.app_href,
            body=json.dumps({'account': {'href': self.acc_href}}),
            content_type="application/json")

        application = self.client.applications.get(self.app_href)

        email = 'fakeuseragain@mailinator.com'

        acc_body = self.acc_body.copy()
        acc_body['email'] = email
        httpretty.register_uri(httpretty.GET,
            self.acc_href,
            body=json.dumps(acc_body),
            content_type="application/json")

        account = application.send_password_reset_email(email)

        self.assertIsInstance(account, Account)
        self.assertTrue(account.href)
        self.assertEqual(account.email, email)

    @httpretty.activate
    def test_verify_password_reset_token(self):

        httpretty.register_uri(httpretty.GET,
            self.base_href + "/tenants/current",
            body=json.dumps(self.tenant_body),
            content_type="application/json")

        httpretty.register_uri(httpretty.GET,
            self.app_href,
            body=json.dumps(self.app_body),
            content_type="application/json")

        httpretty.register_uri(httpretty.GET,
            self.acc_href,
            body=json.dumps(self.acc_body),
            content_type="application/json")

        application = self.client.applications.get(self.app_href)
        token = 'TOKEN'

        httpretty.register_uri(httpretty.GET,
            "%s/passwordResetTokens/%s" % (self.app_href, token),
            body=json.dumps({'account': {'href': self.acc_href}}),
            content_type="application/json")

        account = application.verify_password_reset_token(token)

        self.assertIsInstance(account, Account)
        self.assertTrue(account.href)
        self.assertTrue(account.givenName)

    @httpretty.activate
    def test_search(self):
        # fetch application
        httpretty.register_uri(httpretty.GET,
            self.base_href + "/tenants/current",
            body=json.dumps(self.tenant_body),
            content_type="application/json")

        httpretty.register_uri(httpretty.GET,
            self.app_href,
            body=json.dumps(self.app_body),
            content_type="application/json")

        application = self.client.applications.get(self.app_href)

        self.resource_body = {
            "href": self.app_href + "/accounts",
            "offset": 0,
            "limit": 25,
            "items": [self.acc_body]
        }

        # search application accounts without attributes
        httpretty.register_uri(httpretty.GET,
            self.app_href + "/accounts",
            body=json.dumps(self.resource_body),
            content_type="application/json")

        accounts = application.accounts.search("ACC_USERNAME")
        for acc in accounts:
            pass

        regex = '\/v1\/applications\/APP_ID\/accounts\?' \
            + '.*((?=.*offset=0)(?=.*limit=25)(?=.*q=ACC_USERNAME).*$)'
        self.assertIsInstance(accounts, AccountResourceList)
        self.assertEqual(HTTPretty.last_request.method, 'GET')
        self.assertIsNotNone(re.search(regex, HTTPretty.last_request.path))

        # search application accounts with attributes
        accounts = application.accounts.search(givenName="ACC_USERNAME")
        for acc in accounts:
            pass

        regex = '\/v1\/applications\/APP_ID\/accounts\?' \
            + '.*((?=.*offset=0)(?=.*limit=25)(?=.*givenName=ACC_USERNAME).*$)'
        self.assertIsInstance(accounts, AccountResourceList)
        self.assertEqual(HTTPretty.last_request.method, 'GET')
        self.assertIsNotNone(re.search(regex, HTTPretty.last_request.path))

        self.resource_body = {
            "href": self.app_href + "/groups",
            "offset": 0,
            "limit": 25,
            "items": [self.grp_body]
        }

        # search application groups without attributes
        httpretty.register_uri(httpretty.GET,
            self.app_href + "/groups",
            body=json.dumps(self.resource_body),
            content_type="application/json")

        groups = application.groups.search("GRP_NAME")
        for group in groups:
            pass

        regex = '\/v1\/applications\/APP_ID\/groups\?' \
            + '.*((?=.*offset=0)(?=.*limit=25)(?=.*q=GRP_NAME).*$)'
        self.assertIsInstance(groups, GroupResourceList)
        self.assertEqual(HTTPretty.last_request.method, 'GET')
        self.assertIsNotNone(re.search(regex, HTTPretty.last_request.path))

        # search application groups with attributes
        groups = application.groups.search(name=self.grp_body['name'])
        for group in groups:
            pass

        regex = '\/v1\/applications\/APP_ID\/groups\?' \
            + '.*((?=.*offset=0)(?=.*limit=25)(?=.*name=GRP_NAME).*$)'
        self.assertIsInstance(groups, GroupResourceList)
        self.assertEqual(HTTPretty.last_request.method, 'GET')
        self.assertIsNotNone(re.search(regex, HTTPretty.last_request.path))

    @httpretty.activate
    def test_associations(self):
        httpretty.register_uri(httpretty.GET,
            self.base_href + "/tenants/current",
            body=json.dumps(self.tenant_body),
            content_type="application/json")

        httpretty.register_uri(httpretty.GET,
            self.tenant_href,
            body=json.dumps(self.tenant_body),
            content_type="application/json")

        httpretty.register_uri(httpretty.GET,
            self.app_href,
            body=json.dumps(self.app_body),
            content_type="application/json")

        application = self.client.applications.get(self.app_href)

        # accounts
        httpretty.register_uri(httpretty.GET,
            self.acc_href,
            body=json.dumps(self.acc_body),
            content_type="application/json")

        account = application.accounts.get(self.acc_href)
        self.assertEqual(account.href, self.acc_href)

        # tenant
        self.assertEqual(application.tenant.name, self.tenant_body["name"])

if __name__ == '__main__':
    unittest.main()

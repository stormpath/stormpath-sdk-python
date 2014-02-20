import unittest
from .test_base import BaseTest
import httpretty
from httpretty import HTTPretty
import json

from stormpath.resources import (Account, AccountList,
    GroupList, PasswordResetTokenList)
from stormpath.error import Error as StormpathError


class TestApplication(BaseTest):

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
            self.app_href,
            body=json.dumps(self.app_body),
            content_type="application/json")

        application = self.client.applications.get(self.app_href)

        self.assertEqual(application.name, self.app_body['name'])
        self.assertEqual(application.description, self.app_body['description'])
        self.assertEqual(application.status, self.app_body['status'])
        self.assertEqual(HTTPretty.last_request.path, self.app_path)

        self.assertIsInstance(application.accounts, AccountList)

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
            self.base_href + "/applications",
            body=json.dumps(self.app_body),
            content_type="application/json")

        application = self.client.applications.create({
            "name": self.dir_body['name'],
            "description": self.dir_body['description'],
            "enabled": self.dir_body['status']
        })

        self.assertEqual(HTTPretty.last_request.method, 'POST')
        self.assertEqual(HTTPretty.last_request.path, '/v1/applications')

        self.assertEqual(application.name, self.app_body['name'])
        self.assertEqual(application.description, self.app_body['description'])
        self.assertEqual(application.status, self.app_body['status'])

    @httpretty.activate
    def test_create_with_directory(self):
        httpretty.register_uri(httpretty.GET,
            self.base_href + "/tenants/current",
            location=self.tenant_href,
            status=302)

        httpretty.register_uri(httpretty.GET,
            self.tenant_href,
            body=json.dumps(self.tenant_body),
            content_type="application/json")

        error = {'moreInfo': 'https://www.stormpath.com/docs/errors/2000',
            'status': 400,
            'code': 2000,
            'message': 'createDirectory query parameter value cannot be ' +
                'null, empty, or blank.',
            'developerMessage': 'createDirectory query parameter value ' +
                'cannot be null, empty, or blank.'
        }

        httpretty.register_uri(httpretty.POST,
            self.base_href + "/applications",
            responses=[
                httpretty.Response(body=json.dumps(self.app_body), status=200),
                httpretty.Response(body=json.dumps(self.app_body), status=200),
                httpretty.Response(body=json.dumps(error), status=400),
            ],
            content_type="application/json")

        application = self.client.applications.create({
            "name": self.dir_body['name'],
            "description": self.dir_body['description'],
            "enabled": self.dir_body['status']
        }, create_directory="Directory")

        self.assertEqual(application.name, self.app_body['name'])
        self.assertEqual(application.description, self.app_body['description'])
        self.assertEqual(application.status, self.app_body['status'])

        self.assertEqual(HTTPretty.last_request.method, 'POST')
        self.assertEqual(HTTPretty.last_request.path,
            '/v1/applications?createDirectory=Directory')

        application = self.client.applications.create({
            "name": self.dir_body['name'],
            "description": self.dir_body['description'],
            "enabled": self.dir_body['status']
        }, create_directory=True)

        self.assertEqual(application.name, self.app_body['name'])
        self.assertEqual(application.description, self.app_body['description'])
        self.assertEqual(application.status, self.app_body['status'])

        self.assertEqual(HTTPretty.last_request.method, 'POST')
        self.assertEqual(HTTPretty.last_request.path,
            '/v1/applications?createDirectory=True')

        with self.assertRaises(StormpathError) as context:
            application = self.client.applications.create({
                "name": self.dir_body['name'],
                "description": self.dir_body['description'],
                "enabled": self.dir_body['status']
            }, create_directory=True)

        exception = context.exception
        self.assertEqual(exception.message, error['message'])

        with self.assertRaises(StormpathError) as context:
            application = self.client.applications.create({
                "name": self.dir_body['name'],
                "description": self.dir_body['description'],
                "enabled": self.dir_body['status']
            }, create_directory="+++++")

        exception = context.exception
        self.assertEqual(exception.message, error['message'])

    @httpretty.activate
    def test_send_password_reset_email(self):
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
        email = 'fakeuseragain@mailinator.com'

        response = {
            "account": {
                "href": self.acc_href
            },
            "email": email,
            "href": self.app_href + "/passwordResetTokens/TOKEN"
        }

        httpretty.register_uri(httpretty.POST,
            "%s/passwordResetTokens" % self.app_href,
            body=json.dumps(response),
            content_type="application/json")

        application = self.client.applications.get(self.app_href)

        httpretty.register_uri(httpretty.GET,
            self.acc_href,
            body=json.dumps(response),
            content_type="application/json")

        account = application.send_password_reset_email(email)

        self.assertIsInstance(application.password_reset_tokens,
            PasswordResetTokenList)
        self.assertIsInstance(account, Account)
        self.assertTrue(account.href)
        self.assertEqual(account.email, email)

    @httpretty.activate
    def test_verify_password_reset_token(self):
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

        self.assertEqual(HTTPretty.last_request.method, 'GET')

        self.assertIsInstance(account, Account)
        self.assertTrue(account.href)
        self.assertTrue(account.given_name)

    @httpretty.activate
    def test_search(self):
        # fetch application
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

        accounts = application.accounts.search(self.acc_body['username'])
        for acc in accounts:
            pass

        self.assertIsInstance(accounts, AccountList)
        self.assertEqual(HTTPretty.last_request.method, 'GET')
        self.assertEqual(HTTPretty.last_request.path,
            "%s/accounts?q=%s" % (self.app_path, self.acc_body['username']))

        # search application accounts with attributes
        accounts = application.accounts.search({
            'given_name': self.acc_body['username']})
        for acc in accounts:
            pass

        self.assertIsInstance(accounts, AccountList)
        self.assertEqual(HTTPretty.last_request.method, 'GET')
        self.assertEqual(HTTPretty.last_request.path,
            "%s/accounts?givenName=%s" % (self.app_path,
                                        self.acc_body['username']))

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

        groups = application.groups.search(self.grp_body['name'])
        for group in groups:
            pass

        self.assertIsInstance(groups, GroupList)
        self.assertEqual(HTTPretty.last_request.method, 'GET')
        self.assertEqual(HTTPretty.last_request.path,
            "%s/groups?q=%s" % (self.app_path, self.grp_body['name']))

        # search application groups with attributes
        groups = application.groups.search({
            'name': self.grp_body['name']})
        for group in groups:
            pass

        self.assertIsInstance(groups, GroupList)
        self.assertEqual(HTTPretty.last_request.method, 'GET')
        self.assertEqual(HTTPretty.last_request.path,
            "%s/groups?name=%s" % (self.app_path, self.grp_body['name']))

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

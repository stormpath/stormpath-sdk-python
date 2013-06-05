import unittest
from tests.test_base import BaseTest
import httpretty
import json

from stormpath.auth import UsernamePasswordRequest


class TestAccount(BaseTest):

    @httpretty.activate
    def test_save(self):

        httpretty.register_uri(httpretty.GET,
            self.base_url + "/tenants/current",
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
            "status": "ENABLED",
            "groups": {
                "href": self.acc_href + "/groups"
                },
            "groupMemberships": {
                "href": self.acc_href + "groupMemberships"
                },
                "directory": {
                    "href": self.dir_href
                    },
                    "tenant": {
                        "href": self.base_url + "/tenants/TENANT_ID"
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
            "status": "ENABLED",
            "groups": {
                "href": self.acc_href + "/groups"
                },
            "groupMemberships": {
                "href": self.acc_href + "groupMemberships"
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
            self.acc_href,
            body=json.dumps(body),
            content_type="application/json")

        username = 'superuser123changed' 'User Changed'
        email = 'superuser123changed@superemail.comy'
        given_name = 'Super Changed'
        surname = 'User Changed'
        password = 'superP4ssChanged'

        account.username = username
        account.email = email
        account.given_name = given_name
        account.surname = surname
        account.password = password
        account.middle_name = 'middle'

        account.save()

        self.assertEqual(account.username, username)
        self.assertEqual(account.email, email)
        self.assertEqual(account.given_name, given_name)
        self.assertEqual(account.surname, surname)
        self.assertEqual(account.middle_name, 'middle')

    @httpretty.activate
    def test_create(self):

        httpretty.register_uri(httpretty.GET,
            self.base_url + "/tenants/current",
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
            "status": "ENABLED",
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

        self.assertEqual(account.username, username)
        self.assertEqual(account.email, email)
        self.assertEqual(account.given_name, given_name)
        self.assertEqual(account.surname, surname)

    @httpretty.activate
    def test_authenticate(self):
        auth_request = UsernamePasswordRequest("USERNAME", "PASSWORD")

        httpretty.register_uri(httpretty.GET,
            self.base_url + "/tenants/current",
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

        application = self.client.applications.get(self.app_href)
        auth_result = application.authenticate_account(auth_request)
        account = auth_result.account
        self.assertEqual(application.href, self.app_href)
        self.assertEqual(account.href, self.acc_href)

if __name__ == '__main__':
    unittest.main()

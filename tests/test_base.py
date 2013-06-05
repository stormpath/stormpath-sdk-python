import unittest
import httpretty

from stormpath.clients import Client


class BaseTest(unittest.TestCase):
    @httpretty.activate
    def setUp(self):

        self.base_url = "https://api.stormpath.com/v1"

        self.id = 'KEY_ID'
        self.secret = 'KEY_SECRET'
        self.app_href = self.base_url + '/applications/APP_HREF'
        self.dir_href = self.base_url + '/directories/DIR_HREF'
        self.acc_href = self.base_url + '/accounts/ACC_HREF'

        self.tenant_body = {
            "href": "TENANT_HREF",
            "name": "TENANT_NAME",
            "key": "TENANT_KEY",
            "applications":
                {
                    "href": self.base_url + "/tenants/TENANT_ID/applications"
                },
            "directories":
                {
                    "href": self.base_url + "/tenants/TENANT_ID/directories"
                }
            }

        self.dir_body = {
            "href": self.dir_href,
            "name": "DIR_NAME", "description": "DIR_DESC",
            "status": "ENABLED",
            "tenant": {
                "href": self.base_url + "/tenants/TENANT_ID"},
            "accounts": {
                "href": self.dir_href + "/accounts"
                },
            "groups": {
                "href": self.dir_href + "/groups"
                }
            }

        self.app_body = {
            "href": self.app_href,
            "name": "APP_NAME", "description": "APP_DESC",
            "status": "ENABLED",
            "tenant": {
                "href": self.base_url + "/tenants/TENANT_ID"},
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

        self.client = Client(api_key={'id': self.id, 'secret': self.secret})

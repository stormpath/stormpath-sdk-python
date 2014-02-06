import unittest
from stormpath.client import Client


class BaseTest(unittest.TestCase):
    def setUp(self):

        self.base_path = "/v1"
        self.base_url = "https://api.stormpath.com"
        self.base_href = self.base_url + self.base_path

        self.id = 'KEY_ID'
        self.secret = 'KEY_SECRET'

        self.tenant_path = self.base_path + "/tenants/TENANT_ID"
        self.tenant_href = self.base_url + self.tenant_path

        self.app_path = self.base_path + '/applications/APP_ID'
        self.app_href = self.base_url + self.app_path

        self.dir_path = self.base_path + '/directories/DIR_ID'
        self.dir_href = self.base_url + self.dir_path

        self.acc_path = self.base_path + '/accounts/ACC_ID'
        self.acc_href = self.base_url + self.acc_path

        self.grp_path = self.base_path + '/groups/GRP_ID'
        self.grp_href = self.base_url + self.grp_path

        self.map_path = self.base_path + '/accountStoreMappings/MAP_ID'
        self.map_href = self.base_url + self.map_path

        self.custom_path = self.acc_path + '/customData'
        self.custom_href = self.base_url + self.custom_path

        self.tenant_body = {
            "href": "TENANT_HREF",
            "name": "TENANT_NAME",
            "key": "TENANT_KEY",
            "applications": {
                "href": self.tenant_href + "/applications"
            },
            "directories": {
                "href": self.tenant_href + "/directories"
            }
        }

        self.dir_body = {
            "href": self.dir_href,
            "name": "DIR_NAME", "description": "DIR_DESC",
            "status": "ENABLED",
            "tenant": {
                "href": self.tenant_href
            },
            "accounts": {
                "href": self.dir_href + "/accounts"
            },
            "groups": {
                "href": self.dir_href + "/groups"
            }
        }

        self.app_body = {
            "href": self.app_href,
            "name": "APP_NAME",
            "description": "APP_DESC",
            "status": "ENABLED",
            "tenant": {
                "href": self.tenant_href
            },
            "accounts": {
                "href": self.app_href + "/accounts"
            },
            "groups": {
                "href": self.app_href + "/groups"
            },
            "passwordResetTokens": {
                "href": self.app_href + "/passwordResetTokens"
            },
            "loginAttempts": {
                "href": self.app_href + "/loginAttempts"
            }
        }

        self.acc_body = {
            "href": self.acc_href,
            "username": "ACC_USERNAME",
            "email": "ACC_EMAIL",
            "fullName": "ACC_FULLNAME",
            "givenName": "ACC_GIVENNAME",
            "middleName": "",
            "surname": "ACC_SURNAME",
            "status": "ENABLED",
            "customData": {"href": self.custom_href},
            "groups": {
                "href": self.grp_href
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

        self.grp_body = {
            "href": self.grp_href,
            "name": "GRP_NAME",
            "description": "GRP_DESC",
            "status": "ENABLED",
            "customData": {"href": self.custom_href},
            "directory": {
                "href": self.dir_href
            },
            "tenant": {
                "href": self.tenant_href
            },
            "accounts": {
                "href": self.grp_href + "/accounts"
            },
            "groupMemberships": {
                "href": self.grp_href + "/groupMemberships"
            }
        }

        self.map_body = {
            "href": self.map_href,
            "accountStore": {
                "href": self.dir_href
            },
            "application": {
                "href": self.app_href
            },
            "listIndex": 1,
            "isDefaultAccountStore": True,
            "isDefaultGroupStore": True
        }

        self.custom_body = {
            "href": self.custom_href,
            "createdAt": "2014-07-16T13:48:22.378Z",
            "modifiedAt": "2014-07-16T13:48:22.378Z",
            "rank": "Captain",
            "birthDate": "2305-07-13",
            "birthPlace": "La Barre, France",
            "favoriteDrink": "Earl Grey tea"
        }

        self.client = Client(api_key={'id': self.id, 'secret': self.secret})

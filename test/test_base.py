__author__ = 'ecrisostomo'

from unittest import TestCase

from stormpath.client.client import Client, ApiKey

class BaseTest(TestCase):

    def setUp(self):
        self.created_accounts = []
        self.created_applications = []
        self.created_directories = []
        self.created_group_memberships = []
        self.created_groups = []
        id, secret = 'id', 'secret'
        self.client = Client(api_key=ApiKey(id=id, secret=secret), base_url='http://localhost:8080/v1')

    def tearDown(self):

        for grp_ms in self.created_group_memberships:
            self.client.data_store.delete(grp_ms)

        for grp in self.created_groups:
            self.client.data_store.delete(grp)

        for acc in self.created_accounts:
            self.client.data_store.delete(acc)

        for app in self.created_applications:
            self.client.data_store.delete(app)

        for dir in self.created_directories:
            self.client.data_store.delete(dir)

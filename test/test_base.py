__author__ = 'ecrisostomo'

from os.path import expanduser
from unittest import TestCase

from stormpath.client import ClientBuilder

class BaseTest(TestCase):

    def setUp(self):
        self.created_accounts = []
        self.created_applications = []
        self.created_directories = []
        self.created_group_memberships = []
        self.created_groups = []
        location = expanduser('~') + '/.stormpath/apiKey.yml'
        self.client = ClientBuilder().set_base_url('http://localhost:8080/v1').set_api_key_file_location(location).build()

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

class BaseClientBuilder(TestCase):

    def setUp(self):
        self.api_key_file = 'test/apiKey.yml'
        self.ap_key_remote_file = 'http://localhost/apiKey.yml'

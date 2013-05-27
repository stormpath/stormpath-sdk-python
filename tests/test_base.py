import unittest

from stormpath.clients import Client


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.created_accounts = []
        self.created_applications = []
        self.created_directories = []
        self.created_group_memberships = []
        self.created_groups = []
        self.id = '2GOC9ROK2X65D46TDOJZS4W92'
        self.secret = 'vvcLLmoCoE+BsA8Xg2Xz2SlglfgWloyWvx56TQfmxpY'
        self.client = Client(api_key={'id': self.id, 'secret': self.secret})
        self.app_href = 'https://api.stormpath.com/v1/applications/5axrt89PmoFCDldOxpkXgq'
        self.dir_href = 'https://api.stormpath.com/v1/directories/3oqvzGhrKYB1Gg9liJTQnL'

    def tearDown(self):

        for acc in self.created_accounts:
            self.client.data_store.delete(acc)

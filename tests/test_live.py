import os
import unittest
from uuid import uuid4

from stormpath.client import Client
from stormpath.error import Error
from stormpath.resources.group_membership import GroupMembership
from stormpath.resources.base import Expansion


class LiveTest(unittest.TestCase):

    def generate_name(self, prefix):
        return prefix + '_' + str(uuid4())

    def setUp(self):
        self.apiKeyId = os.getenv("STORMPATH_SDK_TEST_API_KEY_ID")
        self.apiKeySecret = os.getenv("STORMPATH_SDK_TEST_API_KEY_SECRET")
        self.client = Client(
            api_key={'id': self.apiKeyId, 'secret': self.apiKeySecret})

        self.created_accounts = []
        self.created_applications = []
        self.created_directories = []
        self.created_group_memberships = []
        self.created_groups = []
        self.created_account_stores = []

    def test_live(self):
        # test directory creation
        name = self.generate_name("my_dir")
        directory = self.client.directories.create({
            'name': name,
            'description': "This is my raindir!"
        })
        self.created_directories.append(directory)
        self.assertEqual(directory.name, name)
        self.assertTrue(directory.is_enabled())

        # test existing directory creation
        with self.assertRaises(Error):
            application = self.client.directories.create({
                "name": name})
            self.created_applications.append(application)

        # test directory group creation
        group_name = self.generate_name("my_group_1")
        group = directory.groups.create({
            "name": group_name,
            "description": "This is my support group",
            "enabled": "enabled"
        })
        self.created_groups.append(group)

        self.assertEqual(group.name, group_name)
        self.assertEqual(group.description, "This is my support group")
        self.assertTrue(group.is_enabled())

        # test directory account creation
        username = self.generate_name("william")
        account = directory.accounts.create({
            'username': username,
            'email': username + "@titan.com",
            'given_name': "William",
            'middle_name': "Thomas",
            'surname': "Riker",
            'password': "xaiK3auc",
            "custom_data": {
                "rank": "Captain",
                "birthDate": "2305-07-13",
                "birthPlace": "La Barre, France",
                "favoriteDrink": "Earl Grey tea"
            }
        })

        self.assertTrue(account.is_enabled())

        # test custom data
        account.custom_data['birthDate'] = 'whenever'
        self.assertEqual(account.custom_data['rank'], 'Captain')
        self.assertEqual(account.custom_data['birthDate'], 'whenever')
        account.custom_data.save()

        account = directory.accounts.get(account.href)
        self.assertEqual(account.custom_data['birthDate'], 'whenever')
        del account.custom_data['birthDate']
        with self.assertRaises(KeyError):
            account.custom_data['birthDate']
        account = directory.accounts.get(account.href)
        self.assertEqual(account.custom_data['birthDate'], "whenever")
        del account.custom_data['birthDate']
        account.custom_data.save()
        account = directory.accounts.get(account.href)
        with self.assertRaises(KeyError):
            account.custom_data['birthDate']

        # test application creation
        name = self.generate_name("my_app")
        application = self.client.applications.create({
            "name": name,
            "description": "This is my rainapp",
            "enabled": "enabled"
        })
        self.created_applications.append(application)

        # test invalid application authentication
        with self.assertRaises(Error):
            account = application.authenticate_account(username, "xaiK3auc")

        # test application creation with directory
        app_name = self.generate_name("my_app")
        dir_name = self.generate_name("my_dir")
        application2 = self.client.applications.create({
            "name": app_name,
            "description": "This is my rainapp",
            "enabled": "enabled"
        }, create_directory=dir_name)
        self.created_applications.append(application2)

        self.assertEqual(application2.name, app_name)
        self.assertEqual(application2.description, "This is my rainapp")
        self.assertTrue(application2.is_enabled())
        directory2 = self.client.directories.search({"name": dir_name})[0]
        self.created_directories.append(directory2)
        self.assertEqual(directory2.name, dir_name)
        self.assertTrue(directory2.is_enabled())

        # test account to group addition
        group_membership = group.add_account(account)
        self.created_group_memberships.append(group_membership)

        self.assertIsInstance(group_membership, GroupMembership)
        self.assertEqual(
            group_membership.account.email, username + "@titan.com")
        self.assertEqual(group_membership.group.name, group_name)

        # test account store creation
        account_store_mapping = self.client.account_store_mappings.create({
            'application': application, 'account_store': directory})
        self.created_account_stores.append(account_store_mapping)
        self.assertFalse(account_store_mapping.is_default_account_store)

        # test valid application authentication
        login_attempt = application.authenticate_account(username, "xaiK3auc")
        account = login_attempt.account
        self.assertEqual(account.email, username + "@titan.com")
        self.assertEqual(account.middle_name, "Thomas")

        # test unsuccesful account creation on application
        username2 = self.generate_name("ltcmdata")
        with self.assertRaises(Error):
            application.accounts.create({
                'username': username2,
                'email': username2 + "@enterprise.com",
                'given_name': "Lieutenant",
                'surname': "Commander",
                'password': "xaiK3auc"
            })

        # test default account store
        account_store_mapping.is_default_account_store = True
        account_store_mapping.save()
        account2 = application.accounts.create(
            {
                'username': username2,
                'email': username2 + "@enterprise.com",
                'given_name': "Lieutenant",
                'surname': "Commander",
                'password': "xaiK3auc"
            })
        self.created_accounts.append(account2)
        self.assertEqual(account2.email, username2 + "@enterprise.com")
        self.assertIsNone(account2.middle_name, None)

        # test unsuccesful group creation on application
        group2_name = self.generate_name("Android civil rights group")
        with self.assertRaises(Error):
            application.groups.create({
                'name': group2_name
            })

        # test default group store
        account_store_mapping.is_default_group_store = True
        account_store_mapping.save()
        group2 = application.groups.create({
            'name': group2_name
        })
        self.created_groups.append(group2)
        self.assertEqual(group2.name, group2_name)

        # create multiple groups to test on
        for i in range(0, 8):
            group = directory.groups.create(
                {
                    'name': "test_groupi_{0}".format(i),
                    'description': 'random_groups'
                })
            self.created_groups.append(group)

        # test pagination
        groups = directory.groups.search({"description": "random_groups"})
        self.assertEqual(len(groups), 8)
        self.assertEqual(len(groups[3:10]), 5)

        # test expansion
        expansion = Expansion('accounts', 'groups')
        expansion.add_property('groups', offset=0, limit=3)
        directory = self.client.directories.get(directory.href, expansion)
        self.assertEqual(len(directory.groups), 3)

        # test sorting
        groups = directory.groups.order("description asc")
        self.assertEqual(groups[-1].description, "This is my support group")
        groups = directory.groups.order("description desc")
        self.assertEqual(groups[0].description, "This is my support group")

        # test search
        groups = directory.groups.search({"description": "random_groups"})
        self.assertTrue(len(groups), 7)
        groups = directory.groups.search(
            {"description": "random_groups", "name": "test_groupi_1"})
        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0].name, "test_groupi_1")

        # test in_group assertion
        group = directory.groups.search({"description": "random_groups", "name": "test_groupi_1"})[0]
        self.assertFalse(account.in_group(group))
        account.add_group(group)
        self.assertTrue(account.in_group(group))

        # test in_groups assertion
        group1 = directory.groups.search({"description": "random_groups", "name": "test_groupi_1"})[0]
        group2 = directory.groups.search({"description": "random_groups", "name": "test_groupi_2"})[0]
        group3 = directory.groups.search({"description": "random_groups", "name": "test_groupi_2"})[0]
        self.assertFalse(account.in_groups([group1, group2, group3]))
        self.assertTrue(account.in_groups([group1, group2, group3], all=False))
        account.add_group(group2)
        account.add_group(group3)
        self.assertTrue(account.in_groups([group1, group2, group3]))
        self.assertTrue(account.in_groups([group1, group2, group3], all=False))


    def tearDown(self):
        for grp_ms in self.created_group_memberships:
            grp_ms.delete()

        for grp in self.created_groups:
            grp.delete()

        for acc in self.created_accounts:
            acc.delete()

        for app in self.created_applications:
            app.delete()

        for dir in self.created_directories:
            dir.delete()

        for acc_store in self.created_account_stores:
            acc_store.delete()

if __name__ == '__main__':
    unittest.main()

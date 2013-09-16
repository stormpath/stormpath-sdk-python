import os
import unittest

from stormpath.client import Client
from stormpath.error import Error
from stormpath.resource.group_membership import GroupMembership
from stormpath.resource.base import Expansion


class LiveTest(unittest.TestCase):

    def setUp(self):
        self.apiKeyId = os.getenv("STORMPATH_SDK_TEST_API_KEY_ID")
        self.apiKeySecret = os.getenv("STORMPATH_SDK_TEST_API_KEY_SECRET")
        self.client = Client(api_key={'id': self.apiKeyId,
            'secret': self.apiKeySecret})

        self.created_accounts = []
        self.created_applications = []
        self.created_directories = []
        self.created_group_memberships = []
        self.created_groups = []
        self.created_account_stores = []

    def test_live(self):
        # test directory creation
        directory = self.client.directories.create({
            'name': "my_dir_1",
            'description': "This is my raindir!"
            })
        self.created_directories.append(directory)
        self.assertEqual(directory.name, "my_dir_1")
        self.assertTrue(directory.is_enabled())

        # test existing directory creation
        with self.assertRaises(Error):
            application = self.client.directories.create({
                "name": "my_dir_1"})
            self.created_applications.append(application)

        # test directory group creation
        group = directory.groups.create({
            "name": "my_group_1",
            "description": "This is my support group",
            "enabled": "enabled"
        })
        self.created_groups.append(group)

        self.assertEqual(group.name, "my_group_1")
        self.assertEqual(group.description, "This is my support group")
        self.assertTrue(group.is_enabled())

        # test directory account creation
        account = directory.accounts.create({
            'username': "wriker",
            'email': "wriker@titan.com",
            'given_name': "William",
            'middle_name': "Thomas",
            'surname': "Riker",
            'password': "xaiK3auc"
        })

        self.assertTrue(account.is_enabled())

        # test application creation
        application = self.client.applications.create({
            "name": "my_app_1",
            "description": "This is my rainapp",
            "enabled": "enabled"
        })
        self.created_applications.append(application)

        # test invalid application authentication
        with self.assertRaises(Error):
            account = application.authenticate_account("wriker", "xaiK3auc")

        # test application creation with directory
        application2 = self.client.applications.create({
            "name": "my_app_2",
            "description": "This is my rainapp",
            "enabled": "enabled"
        }, create_directory="my_dir_2")
        self.created_applications.append(application2)

        self.assertEqual(application.name, "my_app_1")
        self.assertEqual(application.description, "This is my rainapp")
        self.assertTrue(application.is_enabled())
        directory2 = self.client.directories.search({"name": "my_dir_2"})[0]
        self.created_directories.append(directory2)
        self.assertEqual(directory2.name, "my_dir_2")
        self.assertTrue(directory2.is_enabled())

        # test account to group addition
        group_membership = group.add_account(account)
        self.created_group_memberships.append(group_membership)

        self.assertIsInstance(group_membership, GroupMembership)
        self.assertEqual(group_membership.account.email, "wriker@titan.com")
        self.assertEqual(group_membership.group.name, "my_group_1")

        # test account store creation
        account_store_mapping = self.client.account_store_mappings.create({
            'application': application, 'account_store': directory})
        self.created_account_stores.append(account_store_mapping)
        self.assertFalse(account_store_mapping.is_default_account_store)

        # test valid application authentication
        account = application.authenticate_account("wriker", "xaiK3auc")
        self.assertEqual(account.email, "wriker@titan.com")
        self.assertEqual(account.middle_name, "Thomas")

        # test unsuccesful account creation on application
        with self.assertRaises(Error):
            application.accounts.create({
                'username': "ltcmdata",
                'email': "data@enterprise.com",
                'given_name': "Lieutenant",
                'surname': "Commander",
                'password': "xaiK3auc"
            })

        # test default account store
        account_store_mapping.is_default_account_store = True
        account_store_mapping.save()
        account2 = application.accounts.create({
                'username': "ltcmdata",
                'email': "data@enterprise.com",
                'given_name': "Lieutenant",
                'surname': "Commander",
                'password': "xaiK3auc"
            })
        self.created_accounts.append(account2)
        self.assertEqual(account2.email, "data@enterprise.com")
        self.assertIsNone(account2.middle_name, None)

        # test unsuccesful group creation on application
        with self.assertRaises(Error):
            application.groups.create({
                'name': 'Android civil rights group'
            })

        # test default group store
        account_store_mapping.is_default_group_store = True
        account_store_mapping.save()
        group2 = application.groups.create({
            'name': 'Android civil rights group'
        })
        self.created_groups.append(group2)
        self.assertEqual(group2.name, "Android civil rights group")

        # test search
        group = self.client.directories[0].groups.search("my_group_1")
        self.assertEqual(group[0].account_memberships[0].account.username,
            "wriker")

        # create multiple groups to test on
        for i in range(0, 8):
            group = directory.groups.create(
                {'name': 'test_groupi_{0}'.format(i),
                'description': 'random_groups'})
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

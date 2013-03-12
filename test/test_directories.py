__author__ = 'ecrisostomo'

from test.test_base import BaseTest
from stormpath.resource import Account, AccountList, Directory,  Group, GroupList, Tenant, enabled, disabled

class DirectoriesTest(BaseTest):

    def test_properties(self):
        dir_name, dir_desc = "New Dir Name", "New Dir Desc"
        directory = self._create_directory_(dir_name, dir_desc)

        self.assertEqual(directory.name, dir_name)
        self.assertEqual(directory.description, dir_desc)
        self.assertIsInstance(directory.status, enabled.__class__)
        self.assertIsInstance(directory.accounts, AccountList)
        self.assertIsInstance(directory.groups, GroupList)
        self.assertIsInstance(directory.tenant, Tenant)

    def test_update_attributes(self):
        dir_name, dir_desc = "New Dir Name", "New Dir Desc"
        directory = self._create_directory_(dir_name, dir_desc)

        dir_name, dir_desc, status = "Updated Dir Name", "Updated Dir Desc", disabled
        directory.name = dir_name
        directory.description = dir_desc
        directory.status = status
        directory.save()
    
        self.assertEqual(directory.name, dir_name)
        self.assertEqual(directory.description, dir_desc)
        self.assertEqual(directory.status, status)
        self.assertIsInstance(directory.status, disabled.__class__)

    def test_create_account(self):
        dir_name, dir_desc = "New Dir Name", "New Dir Desc"
        directory = self._create_directory_(dir_name, dir_desc)

        email = "newuser@superenterprise.comy"
        acc_props =  {
            "username" : "newusername",
            "email" : email,
            "givenName" : "Plist",
            "surname" : "Machr",
            "password" : "uGhd%a8Kl!"
        }
        account = self.client.data_store.instantiate(Account, acc_props)
        directory.create_account(account)

        self.created_accounts.append(account)

        self.assertIsInstance(account, Account)
        self.assertEqual(account.email, email)
        self.assertTrue(account.href)


    def test_create_account_workflow_disabled(self):
        dir_name, dir_desc = "New Dir Name", "New Dir Desc"
        directory = self._create_directory_(dir_name, dir_desc)

        email = "newuser@superenterprise.comy"
        acc_props =  {
            "username" : "newusername",
            "email" : email,
            "givenName" : "Plist",
            "surname" : "Machr",
            "password" : "uGhd%a8Kl!"
        }
        account = self.client.data_store.instantiate(Account, acc_props)
        directory.create_account(account, False)

        self.created_accounts.append(account)

        self.assertIsInstance(account, Account)
        self.assertEqual(account.email, email)
        self.assertTrue(account.href)

    def test_create_group(self):
        dir_name, dir_desc = "New Dir Name", "New Dir Desc"
        directory = self._create_directory_(dir_name, dir_desc)

        name = "New group name"
        group = self.client.data_store.instantiate(Group, {"name" : name})
        directory.create_group(group)

        self.created_groups.append(group)

        self.assertIsInstance(group, Group)
        self.assertEqual(group.name, name)
        self.assertTrue(group.href)

    def _create_directory_(self, name, description = None, status = enabled):
        directory = self.client.data_store.instantiate(Directory)
        directory.name = name
        directory.description = description
        directory.status = status

        self.client.data_store.create('directories', directory, Directory)

        self.created_directories.append(directory)

        return directory

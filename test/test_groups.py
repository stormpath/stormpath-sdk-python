__author__ = 'ecrisostomo'

from test.test_base import BaseTest
from stormpath.resource import Account, AccountList, Group, GroupMembership, Directory, Tenant, enabled, disabled


class GroupsTest(BaseTest):

    def test_properties(self):
        name, desc, dir_name = 'New Group Name', 'New Group Desc', 'New dir for group'
        group = self._create_group_(name, desc, dir_name)

        self.assertEqual(group.name, name)
        self.assertEqual(group.description, desc)
        self.assertEquals(group.directory.name, dir_name)
        self.assertIsInstance(group.status, enabled.__class__)
        self.assertIsInstance(group.directory, Directory)
        self.assertIsInstance(group.accounts, AccountList)
        self.assertIsInstance(group.tenant, Tenant)

    def test_update_attributes(self):
        name, desc, dir_name = 'New Group Name', 'New Group Desc', 'New dir for group'
        group = self._create_group_(name, desc, dir_name)

        name, desc, status = 'Updated Group Name', 'Updated Group Desc', disabled

        group.name = name
        group.description = desc
        group.status = disabled
        group.save()

        self.assertEqual(group.name, name)
        self.assertEqual(group.description, desc)
        self.assertEqual(group.status, status)
        self.assertIsInstance(group.status, disabled.__class__)

    def test_add_account(self):
        name, desc, dir_name = 'New Group Name', 'New Group Desc', 'New dir for group'
        group = self._create_group_(name, desc, dir_name)

        email = 'whateveremailthisis@mysuperdomain234.comy'
        acc_props =  {
            "email" : email,
            "givenName" : "Given Name",
            "surname" : "Surname",
            "password" : "superP4ss"
        }

        account = self.client.data_store.instantiate(Account, acc_props)
        group.directory.create_account(account)

        group_membership = group.add_account(account)

        self.created_accounts.append(account)
        self.created_group_memberships.append(group_membership)

        self.assertIsInstance(group_membership, GroupMembership)
        self.assertTrue(group_membership.href)
        self.assertEquals(group_membership.account.email, email)
        self.assertEquals(group_membership.group.name, name)

    def _create_group_(self, name, description, dir_name, status = enabled):

        directory = self.client.data_store.instantiate(Directory)
        directory.name = dir_name

        self.client.data_store.create('directories', directory, Directory)

        self.created_directories.append(directory)

        group = self.client.data_store.instantiate(Group)
        group.name = name
        group.description = description
        group.status = status

        self.created_groups.append(group)

        directory.create_group(group)

        return group

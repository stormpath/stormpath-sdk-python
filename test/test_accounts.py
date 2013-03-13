__author__ = 'ecrisostomo'

from test.test_base import BaseTest

from stormpath.resource import (
    Account, Directory, EmailVerificationToken, Group, GroupList, GroupMembership, GroupMembershipList, enabled, disabled
)

class AccountsTest(BaseTest):

    def test_properties(self):
        username, email, given_name, surname, password, dir_name = 'superuser123', 'superuser123@superemail.comy', 'Super', 'User', 'superP4ss', 'New Dir Name 123 Ha!'
        account = self._create_account(email, given_name, surname, password, username, dir_name)

        self.assertEqual(account.username, username)
        self.assertEqual(account.email, email)
        self.assertEqual(account.given_name, given_name)
        self.assertEqual(account.surname, surname)
        self.assertEqual(account.directory.name, dir_name)
        self.assertIsInstance(account.status, enabled.__class__)
        self.assertIsInstance(account.groups, GroupList)
        self.assertIsInstance(account.directory, Directory)
        self.assertIsInstance(account.group_memberships, GroupMembershipList)
        self.assertTrue(isinstance(account.email_verification_token, EmailVerificationToken) or account.email_verification_token == None)

    def test_update_attributes(self):
        username, email, given_name, surname, password = 'superuser123', 'superuser123@superemail.comy', 'Super', 'User', 'superP4ss'
        account = self._create_account(email, given_name, surname, password, username, 'Whatever dir 123')

        username, email, given_name, surname, password = 'superuser123changed', 'superuser123changed@superemail.comy', 'Super Changed', 'User Changed', 'superP4ssChanged'
        account.username = username
        account.email = email
        account.given_name = given_name
        account.surname = surname
        account.password = password
        account.status = disabled
        account.middle_name = 'middle'
        account.save()

        self.assertEqual(account.username, username)
        self.assertEqual(account.email, email)
        self.assertEqual(account.given_name, given_name)
        self.assertEqual(account.surname, surname)
        self.assertEqual(account.middle_name, 'middle')
        self.assertIsInstance(account.status, disabled.__class__)

    def test_add_group(self):
        username, email, given_name, surname, password = 'superuser123', 'superuser123@superemail.comy', 'Super', 'User', 'superP4ss'
        account = self._create_account(email, given_name, surname, password, username, 'Whatever dir 123')

        group_name = 'New Group Name'
        group = self.client.data_store.instantiate(Group, {"name" : group_name})
        account.directory.create_group(group)

        group_membership = account.add_group(group)

        self.created_groups.append(group)
        self.created_group_memberships.append(group_membership)

        self.assertIsInstance(group_membership, GroupMembership)
        self.assertTrue(group_membership.href)
        self.assertEquals(group_membership.account.email, email)
        self.assertEquals(group_membership.group.name, group_name)

    def _create_account(self, email, given_name, surname, password, username = None, dir_name = None):

        directory = self._create_directory_(dir_name)

        acc_props =  {
            "username" : username if username else email,
            "email" : email,
            "givenName" : given_name,
            "surname" : surname,
            "password" : password
        }

        account = self.client.data_store.instantiate(Account, acc_props)
        directory.create_account(account)

        self.created_accounts.append(account)

        return account

    def _create_directory_(self, name, description = None, status = enabled):
        directory = self.client.data_store.instantiate(Directory)
        directory.name = name
        directory.description = description
        directory.status = status

        self.client.data_store.create('directories', directory, Directory)

        self.created_directories.append(directory)

        return directory

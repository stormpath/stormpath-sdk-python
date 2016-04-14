"""Live tests of Groups functionality."""

from stormpath.error import Error

from .base import SingleApplicationBase, AccountBase


class TestGroups(SingleApplicationBase):

    def test_groups_client_iteration(self):
        for _ in self.client.groups:
            pass

    def test_groups_client_create(self):
        with self.assertRaises(ValueError):
            self.client.groups.create({
                'name': self.get_random_name(),
                'description': 'test group',
            })

    def test_groups_client_get(self):
        group = self.app.groups.create({
            'name': self.get_random_name(),
            'description': 'test group',
        })

        client_group = self.client.groups.get(group.href)

        self.assertEqual(client_group.name, group.name)

    def test_application_group_creation_and_removal(self):
        name = self.get_random_name()

        group = self.app.groups.create({
            'name': name,
            'description': 'test group',
        })

        self.assertTrue(group.is_enabled())
        self.assertEqual(group.directory.href, self.dir.href)

        group2 = self.app.groups.get(group.href)
        self.assertEqual(group.href, group2.href)

        group.delete()

        self.assertEqual(len(self.app.groups.query(name=group.name)), 0)

    def test_directory_group_creation_and_removal(self):
        name = self.get_random_name()

        group = self.dir.groups.create({
            'name': name,
            'description': 'test group',
        })

        self.assertTrue(group.is_enabled())
        self.assertEqual(group.directory.href, self.dir.href)

        group2 = self.dir.groups.get(group.href)
        self.assertEqual(group.href, group2.href)

        group.delete()

        self.assertEqual(len(self.dir.groups.query(name=group.name)), 0)

    def test_group_creation_failure(self):
        name = self.get_random_name()

        self.app.groups.create({
            'name': name,
            'description': 'test group',
        })

        with self.assertRaises(Error):
            self.app.groups.create({
                'name': name,
                'description': 'test group',
            })

    def test_group_modification(self):
        name = self.get_random_name()

        group = self.app.groups.create({
            'name': name,
            'description': 'test group',
        })

        group.description = 'updated desc'
        group.save()

        group2 = self.app.groups.get(group.href)
        self.assertEqual(group2.description, group.description)

    def test_setting_group_as_account_store(self):
        name = self.get_random_name()

        group = self.app.groups.create({
            'name': name,
            'description': 'test group',
        })

        self.app.account_store_mappings.create({
            'application': self.app,
            'account_store': group,
            'is_default_account_store': True
        })

        account_stores = [mapping.account_store.href for mapping in
            self.app.account_store_mappings]
        self.assertTrue(group.href in account_stores)


class TestAccountGroups(AccountBase):

    def create_group(self, name=None, description=None):
        if name is None:
            name = self.get_random_name()
        if description is None:
            description = name

        group = self.app.groups.create({
            'name': name,
            'description': description
        })

        return name, group

    def test_account_group_assignment_and_removal_works(self):
        _, account = self.create_account(self.app.accounts)
        _, group = self.create_group()

        group.add_account(account)
        self.assertTrue(group.has_account(account))
        self.assertTrue(account.has_group(group))

        group.remove_account(account)
        self.assertFalse(group.has_account(account))
        self.assertFalse(account.has_group(group))

        account.add_group(group)
        self.assertTrue(group.has_account(account))
        self.assertTrue(account.has_group(group))

        account.remove_group(group)
        self.assertFalse(group.has_account(account))
        self.assertFalse(account.has_group(group))

    def test_account_group_helpers(self):
        username, account = self.create_account(self.app.accounts)
        _, group = self.create_group()

        group.add_account(username)

        self.assertTrue(group.has_account(account.href))
        self.assertTrue(group.has_accounts([account]))

        self.assertTrue(account.has_group(group.name))
        self.assertTrue(account.has_group(group.href))
        self.assertTrue(account.has_groups([group]))

        account.remove_group(group.href)

    def test_has_multiple_groups_accounts(self):
        _, account1 = self.create_account(self.app.accounts)
        _, group1 = self.create_group()
        _, account2 = self.create_account(self.app.accounts)
        _, group2 = self.create_group()

        group1.add_account(account1)
        self.assertFalse(group1.has_accounts([account1, account2]))
        self.assertTrue(group1.has_accounts([account1, account2], all=False))

        group1.add_account(account2)
        self.assertTrue(group1.has_accounts([account1, account2]))

        self.assertFalse(account1.has_groups([group1, group2]))
        self.assertTrue(account1.has_groups([group1, group2], all=False))

        account1.add_group(group2)
        self.assertTrue(account1.has_groups([group1, group2]))


class TestGroupAccounts(AccountBase):

    def test_resolve_account(self):
        _, account = self.create_account(self.app.accounts)
        group = account.directory.groups.create({'name': self.get_random_name()})

        self.assertEqual(group._resolve_account(account).href, account.href)
        self.assertEqual(group._resolve_account(account.href).href, account.href)
        self.assertEqual(group._resolve_account(account.username).href, account.href)
        self.assertEqual(group._resolve_account(account.email).href, account.href)
        self.assertEqual(group._resolve_account({'username': account.username}).href, account.href)
        self.assertEqual(group._resolve_account({'username': '*' + account.username + '*'}).href, account.href)

    def test_add_accounts(self):
        _, account1 = self.create_account(self.app.accounts)
        _, account2 = self.create_account(self.app.accounts)

        group = account1.directory.groups.create({'name': self.get_random_name()})
        group.add_accounts([account1, account2.href])

        self.assertTrue(group.has_account(account1))
        self.assertTrue(group.has_account(account2))

    def test_remove_accounts(self):
        _, account1 = self.create_account(self.app.accounts)
        _, account2 = self.create_account(self.app.accounts)
        _, account3 = self.create_account(self.app.accounts)

        group = account1.directory.groups.create({'name': self.get_random_name()})
        group.add_accounts([account1, account2.href])
        self.assertTrue(group.has_accounts([account1, account2]))

        group.remove_accounts([account1, account2])
        self.assertFalse(group.has_account(account1))
        self.assertFalse(group.has_account(account2))

        self.assertRaises(Error, group.remove_accounts, [account3])

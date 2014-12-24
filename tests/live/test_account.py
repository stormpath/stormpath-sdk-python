"""Live tests of Accounts and authentication functionality."""

from stormpath.error import Error

from .base import AccountBase


class TestAccountCreateUpdateDelete(AccountBase):

    def test_application_account_creation(self):
        name, acc = self.create_account(self.app.accounts)

        accs = self.app.accounts.query(username=name)

        self.assertEqual(len(accs), 1)
        self.assertEqual(accs[0].username, name)

        dir_accs = self.dir.accounts.query(username=name)

        self.assertEqual(len(dir_accs), 1)
        self.assertEqual(dir_accs[0].username, name)

        accs[0].delete()
        self.assertEqual(len(self.app.accounts.query(username=name)), 0)

    def test_directory_account_creation(self):
        name, acc = self.create_account(self.dir.accounts)

        dir_accs = self.dir.accounts.query(username=name)

        self.assertEqual(len(dir_accs), 1)
        self.assertEqual(dir_accs[0].username, name)

        accs = self.app.accounts.query(username=name)

        self.assertEqual(len(accs), 1)
        self.assertEqual(accs[0].username, name)

        dir_accs[0].delete()
        self.assertEqual(len(self.dir.accounts.query(username=name)), 0)

    def test_duplicate_username_acc_creation_fails(self):
        name, acc = self.create_account(self.app.accounts)

        with self.assertRaises(Error):
            self.create_account(self.app.accounts, username=name)

    def test_duplicate_email_acc_creation_fails(self):
        self.create_account(self.app.accounts, email='foo@example.com')

        with self.assertRaises(Error):
            self.create_account(self.app.accounts, email='foo@example.com')

    def test_account_modification(self):
        name, acc = self.create_account(self.app.accounts)

        acc.email = 'foo@example.com'
        acc.status = acc.STATUS_DISABLED
        acc.save()

        accs = self.app.accounts.query(email=acc.email)

        self.assertEqual(len(accs), 1)
        self.assertFalse(accs[0].is_enabled())


class TestApplicationAuthentication(AccountBase):

    def setUp(self):
        super(TestApplicationAuthentication, self).setUp()
        self.email = self.get_random_name() + '@example.com'
        self.password = 'W00t123!' + self.get_random_name()
        self.username, self.acc = self.create_account(self.app.accounts,
            email=self.email, password=self.password)

    def test_authentication_via_email_succeeds(self):
        result = self.app.authenticate_account(self.email, self.password)
        self.assertEqual(result.account.href, self.acc.href)

    def test_authentication_via_username_succeeds(self):
        result = self.app.authenticate_account(self.username, self.password)
        self.assertEqual(result.account.href, self.acc.href)

    def test_authentication_failure(self):
        with self.assertRaises(Error):
            self.app.authenticate_account(self.username, 'x')


class TestPasswordReset(AccountBase):

    def setUp(self):
        super(TestPasswordReset, self).setUp()
        self.email = 'some@email.com'
        _, self.acc = self.create_account(self.app.accounts, email=self.email)

    def test_password_reset_workflow(self):
        token = self.app.password_reset_tokens.create({'email': self.email})
        self.assertEqual(token.account.href, self.acc.href)

        acc = self.app.verify_password_reset_token(token.token)
        self.assertEqual(acc.href, self.acc.href)

        new_pwd = 'W00t123!' + self.get_random_name()

        self.app.reset_account_password(token.token, new_pwd)

        auth = self.app.authenticate_account(self.acc.username, new_pwd)
        self.assertEqual(auth.account.href, self.acc.href)


class TestAccountGroups(AccountBase):

    def test_resolve_group(self):
        _, account = self.create_account(self.app.accounts)

        group = account.directory.groups.create({'name': 'test_group'})

        self.assertEqual(account._resolve_group(group).href, group.href)
        self.assertEqual(account._resolve_group(group.href).href, group.href)
        self.assertEqual(account._resolve_group(group.name).href, group.href)
        self.assertEqual(account._resolve_group({'name': group.name}).href, group.href)
        self.assertEqual(account._resolve_group({'name': '*' + group.name + '*'}).href, group.href)

    def test_add_groups(self):
        _, account = self.create_account(self.app.accounts)

        group1 = account.directory.groups.create({'name': 'test_group'})
        group2 = account.directory.groups.create({'name': 'test_group2'})

        account.add_groups([group1, group2.href])

        self.assertTrue(account.has_group(group1))
        self.assertTrue(account.has_group(group2))

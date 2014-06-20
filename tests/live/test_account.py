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


class TestCustomData(AccountBase):

    data = {
        'foo': 'F00!',
        'foo_val': 1,
        'fooCamelCase': True,
        'list_of_foo': [
            'a', 1, False, {
                'bar': 1,
                'bar_val': 'value of bar',
                'barCamelCase': True,
                'subBar': {
                    'sub_bar_name': 'Baz',
                    'subBarCamel': 'Quux'
                }
            }
        ]
    }

    def test_account_creation_with_custom_data(self):
        _, acc = self.create_account(self.app.accounts,
            custom_data=self.data)

        acc = self.app.accounts.get(acc.href)
        self.assertEqual(self.data, dict(acc.custom_data))

    def test_custom_data_behaves_as_dict(self):
        _, acc = self.create_account(self.app.accounts,
            custom_data=self.data)

        self.assertEqual(
            set(self.data.keys()),
            set(acc.custom_data.keys()))

        self.assertEqual(
            len(self.data.values()),
            len(acc.custom_data.values()))

        self.assertEqual(
            len(self.data.items()),
            len(acc.custom_data.items()))

        self.assertEqual(set(self.data), set(acc.custom_data))

        self.assertEqual(acc.custom_data['foo'], self.data['foo'])
        self.assertEqual(acc.custom_data.get('foo'), self.data['foo'])
        self.assertEqual(acc.custom_data.get('nonexistent', 42), 42)

    def test_custom_data_modification(self):
        name, acc = self.create_account(self.app.accounts)

        self.assertEqual(dict(acc.custom_data), {})

        acc.custom_data['foo'] = 'F00!'
        acc.custom_data['bar_value'] = 1
        acc.custom_data['bazCamelCase'] = {'a': 1}

        acc.save()

        acc = self.app.accounts.get(acc.href)

        self.assertEqual(acc.custom_data['foo'], 'F00!')
        self.assertEqual(acc.custom_data['bar_value'], 1)
        self.assertEqual(acc.custom_data['bazCamelCase']['a'], 1)

        with self.assertRaises(KeyError):
            acc.custom_data['href'] = 'whatever'
        with self.assertRaises(KeyError):
            acc.custom_data['-foo'] = 'whatever'

        acc.custom_data['foo'] = 'Not Foo anymore!'
        del acc.custom_data['bar_value']

        acc.custom_data.save()

        acc = self.app.accounts.get(acc.href)

        self.assertEqual(acc.custom_data['foo'], 'Not Foo anymore!')
        self.assertFalse('bar_value' in acc.custom_data)


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

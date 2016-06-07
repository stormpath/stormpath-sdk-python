"""Live tests of Accounts and authentication functionality."""

from datetime import datetime

from stormpath.error import Error

from .base import AccountBase
from stormpath.resources.application import ApplicationList
from stormpath.resources.api_key import ApiKeyList


class TestAccountGet(AccountBase):

    def test_account_has_applications(self):
        _, account = self.create_account(self.app.accounts)

        self.assertTrue(hasattr(account, 'applications'))
        self.assertTrue(isinstance(account.applications, ApplicationList))
        self.assertEqual(len(account.applications), 1)
        self.assertEqual(account.applications[0].href, self.app.href)

    def test_account_has_api_keys(self):
        _, account = self.create_account(self.app.accounts)

        self.assertTrue(hasattr(account, 'api_keys'))
        self.assertTrue(isinstance(account.api_keys, ApiKeyList))
        self.assertEqual(len(account.api_keys), 0)

        key = account.api_keys.create()

        self.assertEqual(len(account.api_keys), 1)
        self.assertEqual(account.api_keys[0].href, key.href)


class TestAccountCreateUpdateDelete(AccountBase):

    def test_application_account_creation(self):
        name, _ = self.create_account(self.app.accounts)

        accs = self.app.accounts.query(username=name)

        self.assertEqual(len(accs), 1)
        self.assertEqual(accs[0].username, name)

        dir_accs = self.dir.accounts.query(username=name)

        self.assertEqual(len(dir_accs), 1)
        self.assertEqual(dir_accs[0].username, name)

        accs[0].delete()
        self.assertEqual(len(self.app.accounts.query(username=name)), 0)

    def test_directory_account_creation(self):
        name, _ = self.create_account(self.dir.accounts)

        dir_accs = self.dir.accounts.query(username=name)

        self.assertEqual(len(dir_accs), 1)
        self.assertEqual(dir_accs[0].username, name)

        accs = self.app.accounts.query(username=name)

        self.assertEqual(len(accs), 1)
        self.assertEqual(accs[0].username, name)

        dir_accs[0].delete()
        self.assertEqual(len(self.dir.accounts.query(username=name)), 0)

    def test_directory_account_creation_with_existing_password_hash(self):
        name = self.get_random_name()
        email = name + '@example.com'
        password = "123456"
        # password hash for "123456" password:
        password_hash = "$stormpath2$MD5$1$OWI3OTQwYjEwODEwOTdkNTcwZDY5NjQ2ZDNlNmZjNzM=$ULWTW74NXPyLYj3VfYHWrg=="

        props = {
            'username': name,
            'email': email,
            'given_name': name,
            'surname': name,
            'password': password_hash
        }

        self.dir.accounts.create(props, password_format='mcf')
        dir_accs = self.dir.accounts.query(username=name)

        self.assertEqual(len(dir_accs), 1)
        self.assertEqual(dir_accs[0].username, name)

        accs = self.app.accounts.query(username=name)

        self.assertEqual(len(accs), 1)
        self.assertEqual(accs[0].username, name)

        # account authentication with invalid password raises Error
        with self.assertRaises(Error):
            self.app.authenticate_account(email, 'invalid')

        # check authenticate_account twice - Stormpath uses provided
        # hash the first time, and then recreates the hash
        self.app.authenticate_account(email, password)
        self.app.authenticate_account(email, password)

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

    def test_account_modification_with_custom_data(self):
        name, acc = self.create_account(self.app.accounts)

        acc = self.app.accounts.get(acc.href)

        acc.email = 'foo@example.com'
        acc.status = acc.STATUS_DISABLED
        acc.custom_data['key'] = 'value'
        acc.save()

        accs = self.app.accounts.query(email=acc.email)

        self.assertEqual(len(accs), 1)
        acc = accs[0]
        self.assertEqual(acc.email, 'foo@example.com')
        self.assertEqual(acc.custom_data['key'], 'value')
        self.assertFalse(accs[0].is_enabled())

    def test_account_modification_with_custom_data_and_refresh(self):
        name, acc = self.create_account(self.app.accounts)
        old_email = acc.email

        acc = self.app.accounts.get(acc.href)

        acc.email = 'foo@example.com'
        acc.status = acc.STATUS_DISABLED
        acc.refresh()
        acc.custom_data['key'] = 'value'
        acc.save()

        accs = self.app.accounts.query(email=acc.email)

        self.assertEqual(len(accs), 1)
        acc = accs[0]
        self.assertEqual(acc.email, old_email)
        self.assertEqual(acc.custom_data['key'], 'value')
        self.assertTrue(accs[0].is_enabled())


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

    def test_authentication_via_organization_name_key_succeeds(self):
        name = self.get_random_name()
        name_key = name[:63]

        organization = self.client.tenant.organizations.create({
            'name': name,
            'description': 'test organization',
            'name_key': name_key,
            'status': 'ENABLED'
        })

        oas_mapping = self.client.organization_account_store_mappings.create({
            'account_store': self.dir,
            'organization': organization,
            'list_index': 1,
            'is_default_account_store': True,
            'is_default_group_store': True
        })

        as_mapping = self.client.account_store_mappings.create({
            'account_store': organization,
            'application': self.app,
            'list_index': 1,
            'is_default_account_store': True,
            'is_default_group_store': True
        })

        self.assertTrue(as_mapping.is_default_account_store)
        self.assertTrue(as_mapping.is_default_group_store)
        self.assertEqual(as_mapping.list_index, 1)

        acc_name = self.get_random_name()
        acc_password = 'W00t123!' + acc_name
        acc_email = acc_name + '@example.com'
        acc = organization.accounts.create(
            {
                'surname': acc_name,
                'email': acc_email,
                'password': acc_password,
                'given_name': acc_name
            })

        self.assertTrue(acc.given_name, acc_name)

        result = self.app.authenticate_account(
            acc_email, acc_password, organization_name_key=name_key)

        self.assertEqual(result.account.given_name, acc_name)

        oas_mapping.delete()
        as_mapping.delete()

    def test_authentication_via_organization_name_key_fails(self):
        name = self.get_random_name()
        name_key = name[:63]

        organization = self.client.tenant.organizations.create({
            'name': name,
            'description': 'test organization',
            'name_key': name_key,
            'status': 'ENABLED'
        })

        oas_mapping = self.client.organization_account_store_mappings.create({
            'account_store': self.dir,
            'organization': organization,
            'list_index': 1,
            'is_default_account_store': True,
            'is_default_group_store': True
        })

        as_mapping = self.client.account_store_mappings.create({
            'account_store': organization,
            'application': self.app,
            'list_index': 1,
            'is_default_account_store': True,
            'is_default_group_store': True
        })

        self.assertTrue(as_mapping.is_default_account_store)
        self.assertTrue(as_mapping.is_default_group_store)
        self.assertEqual(as_mapping.list_index, 1)

        acc_name = self.get_random_name()
        acc_password = 'W00t123!' + acc_name
        acc_email = acc_name + '@example.com'
        acc = organization.accounts.create(
            {
                'surname': acc_name,
                'email': acc_email,
                'password': acc_password,
                'given_name': acc_name
            })

        self.assertTrue(acc.given_name, acc_name)

        with self.assertRaises(Error):
            self.app.authenticate_account(
                acc_email, acc_password, organization_name_key='invalid')

        oas_mapping.delete()
        as_mapping.delete()

    def test_authentication_failure(self):
        with self.assertRaises(Error):
            self.app.authenticate_account(self.username, 'x')


class TestPasswordReset(AccountBase):

    def setUp(self):
        super(TestPasswordReset, self).setUp()
        self.email = self.get_random_name() + '@email.com'
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

    def test_send_password_reset_email(self):
        account = self.app.send_password_reset_email(self.email)
        self.assertEqual(account.href, self.acc.href)


class TestAccountGroups(AccountBase):

    def test_resolve_group(self):
        _, account = self.create_account(self.app.accounts)

        group = account.directory.groups.create({'name': self.get_random_name()})

        self.assertEqual(account._resolve_group(group).href, group.href)
        self.assertEqual(account._resolve_group(group.href).href, group.href)
        self.assertEqual(account._resolve_group(group.name).href, group.href)
        self.assertEqual(account._resolve_group({'name': group.name}).href, group.href)
        self.assertEqual(account._resolve_group({'name': '*' + group.name + '*'}).href, group.href)

    def test_add_groups(self):
        _, account = self.create_account(self.app.accounts)

        group1 = account.directory.groups.create({'name': self.get_random_name()})
        group2 = account.directory.groups.create({'name': self.get_random_name()})

        account.add_groups([group1, group2.href])

        self.assertTrue(account.has_group(group1))
        self.assertTrue(account.has_group(group2))

    def test_in_group(self):
        _, account = self.create_account(self.app.accounts)

        group1 = account.directory.groups.create({'name': self.get_random_name()})
        account.add_group(group1)
        self.assertTrue(account.in_group(group1))

    def test_in_groups(self):
        _, account = self.create_account(self.app.accounts)

        group1 = account.directory.groups.create({'name': self.get_random_name()})
        group2 = account.directory.groups.create({'name': self.get_random_name()})

        account.add_groups([group1, group2])
        self.assertTrue(account.in_groups([group1, group2.href]))

    def test_remove_groups(self):
        _, account = self.create_account(self.app.accounts)

        group1 = account.directory.groups.create({'name': self.get_random_name()})
        group2 = account.directory.groups.create({'name': self.get_random_name()})
        group3 = account.directory.groups.create({'name': self.get_random_name()})

        account.add_groups([group1, group2])
        self.assertTrue(account.in_groups([group1, group2.href]))

        account.remove_groups([group1, group2])

        self.assertFalse(account.in_groups([group1, group2]))
        self.assertFalse(account.in_group(group3))

        self.assertRaises(Error, account.remove_groups, [group3])

    def test_iterate_over_groups(self):
        _, account = self.create_account(self.app.accounts)
        groups = []

        for i in range(500):
            groups.append(account.directory.groups.create({'name': self.get_random_name()}))

        for group in groups:
            account.add_group(group)

        account.refresh()

        for group in account.groups:
            self.assertTrue(group.href)


class TestAccountProviderData(AccountBase):

    def test_account_provider_data_get_exposed_readonly_timestamp_attrs(self):
        name, acc = self.create_account(self.app.accounts)
        pd = acc.provider_data

        self.assertEqual(pd.created_at, pd['created_at'])
        self.assertIsInstance(pd.created_at, datetime)
        self.assertEqual(pd.modified_at, pd['modified_at'])
        self.assertIsInstance(pd.modified_at, datetime)

    def test_account_provider_data_modify_exposed_readonly_timestamps(self):
        name, acc = self.create_account(self.app.accounts)
        pd = acc.provider_data

        with self.assertRaises(AttributeError):
            pd.created_at = 'whatever'
        with self.assertRaises(AttributeError):
            pd['created_at'] = 'whatever'
        with self.assertRaises(AttributeError):
            pd.modified_at = 'whatever'
        with self.assertRaises(AttributeError):
            pd['modified_at'] = 'whatever'

        with self.assertRaises(Exception):
            del pd['created_at']
        with self.assertRaises(Exception):
            del pd['modified_at']

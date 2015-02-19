"""Live tests of basic Application and Directory functionality."""

from stormpath.error import Error

from .base import AuthenticatedLiveBase, SingleApplicationBase, AccountBase


class TestApplicationDirectoryCreation(AuthenticatedLiveBase):

    def app_exists(self, name):
        return len(self.client.applications.query(name=name)) == 1

    def dir_exists(self, name):
        return len(self.client.directories.query(name=name)) == 1

    def test_application_creation_and_deletion(self):
        name = self.get_random_name()

        app = self.client.applications.create({
            'name': name,
            'description': 'test app'
        })
        self.assertTrue(self.app_exists(name))

        app.delete()
        self.assertFalse(self.app_exists(name))

    def test_application_and_directory_creation(self):
        name = self.get_random_name()

        app = self.client.applications.create({
            'name': name,
            'description': 'test app'
        }, create_directory=name)
        self.assertTrue(self.app_exists(app.name))

        try:
            self.assertTrue(self.dir_exists(name))
            dir = app.default_account_store_mapping.account_store
            self.assertEqual(dir.name, name)
        finally:
            app.delete()

        dir.delete()

        self.assertFalse(self.app_exists(name))
        self.assertFalse(self.dir_exists(name))

    def test_directory_creation_and_deletion(self):
        name = self.get_random_name()

        dir = self.client.directories.create({
            'name': name,
            'description': 'test dir'
        })
        self.assertTrue(self.dir_exists(name))

        dir.delete()
        self.assertFalse(self.dir_exists(name))

    def test_application_creation_with_existing_name_fails(self):
        name = self.get_random_name()

        app = self.client.applications.create({
            'name': name,
            'description': 'test app'
        })

        try:
            with self.assertRaises(Error):
                self.client.applications.create({
                    'name': name,
                    'description': 'duplicate app'
                })
        finally:
            app.delete()

    def test_directory_creation_with_existing_name_fails(self):
        name = self.get_random_name()

        dir = self.client.directories.create({
            'name': name,
            'description': 'test dir'
        })

        try:
            with self.assertRaises(Error):
                self.client.directories.create({
                    'name': name,
                    'description': 'duplicate dir'
                })
        finally:
            dir.delete()


class TestAccountStoreMappings(AuthenticatedLiveBase):

    def setUp(self):
        super(TestAccountStoreMappings, self).setUp()

        self.app_name = self.get_random_name()
        self.dir_name = self.get_random_name()

        self.app = self.client.applications.create({
            'name': self.app_name,
            'description': 'test app'
        })
        self.dir = self.client.directories.create({
            'name': self.dir_name,
            'description': 'test dir'
        })

    def tearDown(self):
        self.app.delete()
        self.dir.delete()

    def test_application_account_mapping_assignment_and_removal(self):
        self.assertEqual(len(self.app.account_store_mappings), 0)
        self.assertIsNone(self.app.default_account_store_mapping)
        self.assertIsNone(self.app.default_group_store_mapping)

        asm = self.app.account_store_mappings.create({
            'application': self.app,
            'account_store': self.dir,
            'list_index': 0,
            'is_default_account_store': True,
            'is_default_group_store': True
        })

        self.clear_cache()
        self.app = self.client.applications.get(self.app.href)

        self.assertEqual(len(self.app.account_store_mappings), 1)
        self.assertEqual(self.dir.href,
            self.app.default_account_store_mapping.account_store.href)
        self.assertEqual(self.dir.href,
            self.app.default_group_store_mapping.account_store.href)

        asm.is_default_account_store = False
        asm.is_default_group_store = False
        asm.save()

        self.clear_cache()
        self.app = self.client.applications.get(self.app.href)

        self.assertEqual(len(self.app.account_store_mappings), 1)
        self.assertIsNone(self.app.default_account_store_mapping)
        self.assertIsNone(self.app.default_group_store_mapping)

        asm.delete()

        self.clear_cache()
        self.app = self.client.applications.get(self.app.href)

        self.assertEqual(len(self.app.account_store_mappings), 0)
        self.assertIsNone(self.app.default_account_store_mapping)
        self.assertIsNone(self.app.default_group_store_mapping)


class TestApplicationDirectoryModification(SingleApplicationBase):

    def test_application_modification(self):
        self.app.description = 'updated app'
        self.app.save()

        apps = self.client.applications.query(name=self.app.name,
            description='updated app')

        self.assertEqual(len(apps), 1)
        self.assertEqual(apps[0].href, self.app.href)

    def test_directory_modification(self):
        self.dir.description = 'updated dir'
        self.dir.save()

        dirs = self.client.directories.query(name=self.dir.name,
            description='updated dir')

        self.assertEqual(len(dirs), 1)
        self.assertEqual(dirs[0].href, self.dir.href)


class TestApplicationVerificationEmail(AccountBase):

    def test_resend_fails_for_directory_with_disabled_verificiation(self):
        name, acc = self.create_account(self.app.accounts)
        with self.assertRaises(Error):
            self.app.verification_emails.resend(acc, self.dir)

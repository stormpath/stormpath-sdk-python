"""Live tests of basic Application and Directory functionality."""

from stormpath.error import Error

from .base import AuthenticatedLiveBase, SingleApplicationBase, AccountBase
from stormpath.resources import Provider
from stormpath.resources.agent import Agent, AgentConfig, AgentAccountConfig, \
    AgentGroupConfig
from stormpath.resources.email_template import EmailTemplate
from stormpath.resources.password_policy import PasswordPolicy


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


    def test_ldap_directory_creation_and_deletion(self):
        name = self.get_random_name()
        directories_before = len(self.client.directories)

        directory = self.client.directories.create({
            'name': name,
            'description': 'test dir',
            'provider': {
                'provider_id': 'ldap',
                'agent': {
                    'config': {
                        'directory_host': 'ldap.local',
                        'directory_port': '666',
                        'ssl_required': True,
                        'agent_user_dn': 'user@somewhere.com',
                        'agent_user_dn_password': 'Password',
                        'base_dn': 'dc=example,dc=com',
                        'poll_interval': 60,
                        'account_config': {
                            'dn_suffix': 'ou=employees',
                            'object_class': 'person',
                            'object_filter': '(cn=finance)',
                            'email_rdn': 'email',
                            'given_name_rdn': 'givenName',
                            'middle_name_rdn': 'middleName',
                            'surname_rdn': 'sn',
                            'username_rdn': 'uid',
                            'password_rdn': 'userPassword',
                            },
                        'group_config': {
                            'dn_suffix': 'ou=groups',
                            'object_class': 'groupOfUniqueNames',
                            'object_filter': '(ou=*-group)',
                            'name_rdn': 'cn',
                            'description_rdn': 'description',
                            'members_rdn': 'uniqueMember'
                        }
                    }
                }
            }
        })

        self.assertIsNotNone(directory.href)
        self.assertEqual(directory.name, name)
        self.assertIsInstance(directory.provider, Provider)
        self.assertEqual(directory.provider.provider_id, 'ldap')
        self.assertIsInstance(directory.provider.agent, Agent)
        self.assertIsInstance(directory.provider.agent.config, AgentConfig)
        agent_config = directory.provider.agent.config
        self.assertEqual(agent_config.poll_interval, 60)
        self.assertIsInstance(agent_config.account_config, AgentAccountConfig)
        self.assertEqual(agent_config.account_config.email_rdn, 'email')
        self.assertIsInstance(agent_config.group_config, AgentGroupConfig)
        self.assertEqual(agent_config.group_config.name_rdn, 'cn')
        self.assertEqual(len(self.client.directories), directories_before + 1)

        directory.delete()
        self.assertEqual(len(self.client.directories), directories_before)


    def test_ad_directory_creation_and_deletion(self):
        name = self.get_random_name()
        directories_before = len(self.client.directories)

        directory = self.client.directories.create({
            'name': name,
            'description': 'test dir',
            'provider': {
                'provider_id': 'ad',
                'agent': {
                    'config': {
                        'directory_host': 'ldap.local',
                        'directory_port': '666',
                        'ssl_required': True,
                        'agent_user_dn': 'user@somewhere.com',
                        'agent_user_dn_password': 'Password',
                        'base_dn': 'dc=example,dc=com',
                        'poll_interval': 60,
                        'referral_mode': 'ignore',
                        'ignore_referral_issues': False,
                        'account_config': {
                            'dn_suffix': 'ou=employees',
                            'object_class': 'person',
                            'object_filter': '(cn=finance)',
                            'email_rdn': 'email',
                            'given_name_rdn': 'givenName',
                            'middle_name_rdn': 'middleName',
                            'surname_rdn': 'sn',
                            'username_rdn': 'uid',
                            },
                        'group_config': {
                            'dn_suffix': 'ou=groups',
                            'object_class': 'groupOfUniqueNames',
                            'object_filter': '(ou=*-group)',
                            'name_rdn': 'cn',
                            'description_rdn': 'description',
                            'members_rdn': 'uniqueMember'
                        }
                    }
                }
            }
        })

        self.assertIsNotNone(directory.href)
        self.assertEqual(directory.name, name)
        self.assertIsInstance(directory.provider, Provider)
        self.assertEqual(directory.provider.provider_id, 'ad')
        self.assertIsInstance(directory.provider.agent, Agent)
        self.assertIsInstance(directory.provider.agent.config, AgentConfig)
        agent_config = directory.provider.agent.config
        self.assertEqual(agent_config.poll_interval, 60)
        self.assertIsInstance(agent_config.account_config, AgentAccountConfig)
        self.assertEqual(agent_config.account_config.email_rdn, 'email')
        self.assertIsInstance(agent_config.group_config, AgentGroupConfig)
        self.assertEqual(agent_config.group_config.name_rdn, 'cn')
        self.assertEqual(len(self.client.directories), directories_before + 1)

        directory.delete()
        self.assertEqual(len(self.client.directories), directories_before)


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


class TestDirectoryPasswordPolicy(SingleApplicationBase):

    def test_password_policy_properties(self):
        password_policy = self.dir.password_policy

        self.assertTrue(password_policy.href)
        self.assertEqual(
            password_policy.reset_email_status,
            PasswordPolicy.RESET_EMAIL_STATUS_ENABLED)
        self.assertEqual(
            password_policy.reset_success_email_status,
            PasswordPolicy.RESET_EMAIL_STATUS_ENABLED)
        self.assertEqual(password_policy.reset_token_ttl, 24)

        password_policy.reset_email_status = \
            PasswordPolicy.RESET_EMAIL_STATUS_DISABLED
        password_policy.reset_success_email_status = \
            PasswordPolicy.RESET_EMAIL_STATUS_DISABLED
        password_policy.reset_token_ttl = 100
        password_policy.save()

        self.assertEqual(
            password_policy.reset_email_status,
            PasswordPolicy.RESET_EMAIL_STATUS_DISABLED)
        self.assertEqual(
            password_policy.reset_success_email_status,
            PasswordPolicy.RESET_EMAIL_STATUS_DISABLED)
        self.assertEqual(password_policy.reset_token_ttl, 100)

    def test_directory_password_policy_strength(self):
        strength = self.dir.password_policy.strength

        self.assertTrue(strength.href)
        self.assertEqual(strength.min_symbol, 0)
        self.assertEqual(strength.min_diacritic, 0)
        self.assertEqual(strength.min_upper_case, 1)
        self.assertEqual(strength.min_length, 8)
        self.assertEqual(strength.min_lower_case, 1)
        self.assertEqual(strength.max_length, 100)
        self.assertEqual(strength.min_numeric, 1)

        strength.min_symbol = 1
        strength.min_diacritic = 2
        strength.min_upper_case = 3
        strength.min_length = 4
        strength.min_lower_case = 5
        strength.max_length = 20
        strength.min_numeric = 6
        strength.save()

        self.assertEqual(strength.min_symbol, 1)
        self.assertEqual(strength.min_diacritic, 2)
        self.assertEqual(strength.min_upper_case, 3)
        self.assertEqual(strength.min_length, 4)
        self.assertEqual(strength.min_lower_case, 5)
        self.assertEqual(strength.max_length, 20)
        self.assertEqual(strength.min_numeric, 6)

    def test_directory_reset_email_template_list(self):
        templates = self.dir.password_policy.reset_email_templates

        self.assertTrue(templates.href)
        self.assertEqual(templates.limit, 25)
        self.assertEqual(templates.offset, 0)

    def test_directory_reset_email_template(self):
        template = next(iter(self.dir.password_policy.reset_email_templates))

        self.assertTrue(template.href)
        self.assertEqual(template.subject, 'Reset your Password')
        self.assertEqual(
            template.name, 'Default Password Reset Email Template')
        self.assertEqual(
            template.default_model,
            {'linkBaseUrl': 'https://api.stormpath.com/passwordReset'})
        self.assertEqual(
            template.get_link_base_url(),
            'https://api.stormpath.com/passwordReset')

        template.subject = 'New Reset your Password Subject'
        template.name = 'New Default Password Reset Email Template Name'
        template.set_link_base_url(
            'https://api.stormpath.com/newPasswordReset')
        template.save()

        template = next(iter(self.dir.password_policy.reset_email_templates))

        self.assertTrue(template.href)
        self.assertEqual(
            template.default_model,
            {'linkBaseUrl': 'https://api.stormpath.com/newPasswordReset'})
        self.assertEqual(
            template.get_link_base_url(),
            'https://api.stormpath.com/newPasswordReset')
        self.assertEqual(template.subject, 'New Reset your Password Subject')
        self.assertEqual(
            template.name, 'New Default Password Reset Email Template Name')

    def test_directory_reset_email_template_default_model_set_to_empty(self):
        template = next(iter(self.dir.password_policy.reset_email_templates))

        template.default_model = {}
        with self.assertRaises(Error):
            template.save()

    def test_directory_reset_email_template_default_model_modification(self):
        template = next(iter(self.dir.password_policy.reset_email_templates))

        template.default_model = {
            'linkBaseUrl':
                'https://api.stormpath.com/brandNewPasswordReset'
        }
        template.save()

        template = next(iter(self.dir.password_policy.reset_email_templates))

        self.assertEqual(
            template.get_link_base_url(),
            'https://api.stormpath.com/brandNewPasswordReset')
        self.assertEqual(
            template.default_model,
            {
                'linkBaseUrl':
                    'https://api.stormpath.com/brandNewPasswordReset',
            })

    def test_directory_reset_success_email_template_list(self):
        templates = self.dir.password_policy.reset_success_email_templates

        self.assertTrue(templates.href)
        self.assertEqual(templates.limit, 25)
        self.assertEqual(templates.offset, 0)

    def test_directory_reset_success_email_template(self):
        templates = self.dir.password_policy.reset_success_email_templates
        template = next(iter(templates))

        self.assertTrue(template.href)
        self.assertEqual(template.subject, 'Your password has been changed')
        self.assertEqual(
            template.name, 'Default Password Reset Success Email Template')

        template.subject = 'Your password has been reset.'
        template.description = 'My New Description'
        template.from_name = 'John Doe Jr.'
        template.from_email_address = 'joejr@newemail.com'
        template.name = 'New Email Name'
        template.text_body = 'Your password has been successfully reset.'
        template.html_body = \
            'Your password has been <b>successfully</b> reset.'
        template.mime_type = EmailTemplate.MIME_TYPE_HTML
        template.save()

        template = next(iter(templates))

        self.assertTrue(template.href)
        self.assertEqual(template.subject, 'Your password has been reset.')
        self.assertEqual(template.description, 'My New Description')
        self.assertEqual(template.from_name, 'John Doe Jr.')
        self.assertEqual(template.from_email_address, 'joejr@newemail.com')
        self.assertEqual(template.name, 'New Email Name')
        self.assertEqual(
            template.text_body, 'Your password has been successfully reset.')
        self.assertEqual(
            template.html_body,
            'Your password has been <b>successfully</b> reset.')
        self.assertEqual(template.mime_type, EmailTemplate.MIME_TYPE_HTML)

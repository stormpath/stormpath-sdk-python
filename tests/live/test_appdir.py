"""Live tests of basic Application and Directory functionality."""

import datetime

from stormpath.error import Error

from .base import AuthenticatedLiveBase, SingleApplicationBase, AccountBase
from stormpath.resources import (
    AccountCreationPolicy, Provider, SamlPolicy, SamlServiceProvider,
    SsoInitiationEndpoint
)
from stormpath.resources.application import Application
from stormpath.resources.default_relay_state import (
    DefaultRelayState, DefaultRelayStateList
)
from stormpath.resources.tenant import Tenant
from stormpath.resources.agent import (
    Agent, AgentConfig, AgentAccountConfig, AgentGroupConfig
)
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
        self.assertTrue(self.dir_exists(name))

        directory.delete()
        self.assertFalse(self.dir_exists(name))


    def test_ad_directory_creation_and_deletion(self):
        name = self.get_random_name()
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
        self.assertTrue(self.dir_exists(name))

        directory.delete()
        self.assertFalse(self.dir_exists(name))


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

    def test_account_store_mapping_client_iteration(self):
        with self.assertRaises(ValueError):
            for account_store_mapping in self.client.account_store_mappings:
                pass


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
    def test_verification_emails_iteration(self):
        with self.assertRaises(ValueError):
            for verification_email in self.app.verification_emails:
                pass

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


class TestDirectoryAccountCreationPolicy(SingleApplicationBase):

    def test_account_creation_policy_statuses(self):
        account_creation_policy = self.dir.account_creation_policy

        self.assertTrue(account_creation_policy.href)
        self.assertEqual(
            account_creation_policy.verification_email_status,
            AccountCreationPolicy.EMAIL_STATUS_DISABLED)
        self.assertEqual(
            account_creation_policy.verification_success_email_status,
            AccountCreationPolicy.EMAIL_STATUS_DISABLED)
        self.assertEqual(
            account_creation_policy.welcome_email_status,
            AccountCreationPolicy.EMAIL_STATUS_DISABLED)

        account_creation_policy.verification_email_status = \
            AccountCreationPolicy.EMAIL_STATUS_ENABLED
        account_creation_policy.verification_success_email_status = \
            AccountCreationPolicy.EMAIL_STATUS_ENABLED
        account_creation_policy.welcome_email_status = \
            AccountCreationPolicy.EMAIL_STATUS_ENABLED
        account_creation_policy.save()

        self.assertEqual(
            account_creation_policy.verification_email_status,
            AccountCreationPolicy.EMAIL_STATUS_ENABLED)
        self.assertEqual(
            account_creation_policy.verification_success_email_status,
            AccountCreationPolicy.EMAIL_STATUS_ENABLED)
        self.assertEqual(
            account_creation_policy.welcome_email_status,
            AccountCreationPolicy.EMAIL_STATUS_ENABLED)

    def test_directory_verification_email_template(self):
        account_creation_policy = self.dir.account_creation_policy
        templates = account_creation_policy.verification_email_templates

        self.assertTrue(templates.href)
        self.assertEqual(templates.limit, 25)
        self.assertEqual(templates.offset, 0)

        template = next(iter(templates))

        self.assertTrue(template.href)
        self.assertEqual(template.subject, 'Verify your account')
        self.assertEqual(
            template.name, 'Default Verification Email Template')
        self.assertEqual(
            template.default_model,
            {
                'linkBaseUrl':
                    'https://api.stormpath.com/emailVerificationTokens'
            })
        self.assertEqual(
            template.get_link_base_url(),
            'https://api.stormpath.com/emailVerificationTokens')

        template.subject = 'New Verify your account'
        template.name = 'New Default Verification Email Template'
        template.set_link_base_url(
            'https://api.stormpath.com/newEmailVerificationTokens')
        template.save()

        template = next(iter(templates))

        self.assertTrue(template.href)
        self.assertEqual(
            template.default_model,
            {
                'linkBaseUrl':
                    'https://api.stormpath.com/newEmailVerificationTokens'
            })
        self.assertEqual(
            template.get_link_base_url(),
            'https://api.stormpath.com/newEmailVerificationTokens')
        self.assertEqual(template.subject, 'New Verify your account')
        self.assertEqual(
            template.name, 'New Default Verification Email Template')

        template.default_model = {}
        with self.assertRaises(Error):
            template.save()

    def test_directory_verification_success_email_templates(self):
        acp = self.dir.account_creation_policy
        templates = acp.verification_success_email_templates

        self.assertTrue(templates.href)
        self.assertEqual(templates.limit, 25)
        self.assertEqual(templates.offset, 0)

        template = next(iter(templates))

        self.assertTrue(template.href)
        self.assertEqual(template.subject, 'Your account has been confirmed')
        self.assertEqual(
            template.name, 'Default Verification Success Email Template')
        with self.assertRaises(AttributeError):
            template.default_model

        template.subject = 'New Your account has been confirmed'
        template.name = 'New Default Verification Success Email Template'
        template.save()

        template = next(iter(templates))

        self.assertTrue(template.href)
        self.assertEqual(
            template.subject, 'New Your account has been confirmed')
        self.assertEqual(
            template.name, 'New Default Verification Success Email Template')

    def test_directory_verification_email_template(self):
        account_creation_policy = self.dir.account_creation_policy
        templates = account_creation_policy.verification_email_templates

        self.assertTrue(templates.href)
        self.assertEqual(templates.limit, 25)
        self.assertEqual(templates.offset, 0)

        template = next(iter(templates))

        self.assertTrue(template.href)
        self.assertEqual(template.subject, 'Verify your account')
        self.assertEqual(
            template.name, 'Default Verification Email Template')
        self.assertEqual(
            template.default_model,
            {
                'linkBaseUrl':
                    'https://api.stormpath.com/emailVerificationTokens'
            })
        self.assertEqual(
            template.get_link_base_url(),
            'https://api.stormpath.com/emailVerificationTokens')

        template.subject = 'New Verify your account'
        template.name = 'New Default Verification Email Template'
        template.set_link_base_url(
            'https://api.stormpath.com/newEmailVerificationTokens')
        template.save()

        template = next(iter(templates))

        self.assertTrue(template.href)
        self.assertEqual(
            template.default_model,
            {
                'linkBaseUrl':
                    'https://api.stormpath.com/newEmailVerificationTokens'
            })
        self.assertEqual(
            template.get_link_base_url(),
            'https://api.stormpath.com/newEmailVerificationTokens')
        self.assertEqual(template.subject, 'New Verify your account')
        self.assertEqual(
            template.name, 'New Default Verification Email Template')

        template.default_model = {}
        with self.assertRaises(Error):
            template.save()

    def test_directory_welcome_email_templates(self):
        acp = self.dir.account_creation_policy
        templates = acp.welcome_email_templates

        self.assertTrue(templates.href)
        self.assertEqual(templates.limit, 25)
        self.assertEqual(templates.offset, 0)

        template = next(iter(templates))

        self.assertTrue(template.href)
        self.assertEqual(template.subject, 'Your registration was successful')
        self.assertEqual(
            template.name, 'Default Welcome Email Template')
        with self.assertRaises(AttributeError):
            template.default_model

        template.subject = 'New Your registration was successful'
        template.name = 'New Default Welcome Email Template'
        template.save()

        template = next(iter(templates))

        self.assertTrue(template.href)
        self.assertEqual(
            template.subject, 'New Your registration was successful')
        self.assertEqual(
            template.name, 'New Default Welcome Email Template')


class TestApplicationOAuthPolicy(SingleApplicationBase):

    def test_oauth_policy_properties(self):
        oauth_policy = self.app.oauth_policy

        self.assertTrue(oauth_policy.href)
        self.assertTrue(oauth_policy.access_token_ttl)
        self.assertTrue(oauth_policy.refresh_token_ttl)
        self.assertTrue(
            isinstance(oauth_policy.access_token_ttl, datetime.timedelta))
        self.assertTrue(
            isinstance(oauth_policy.refresh_token_ttl, datetime.timedelta))
        self.assertTrue(oauth_policy.token_endpoint)

    def test_oauth_policy_linked_resources(self):
        oauth_policy = self.app.oauth_policy
        application = oauth_policy.application
        tenant = oauth_policy.tenant

        self.assertIsInstance(application, Application)
        self.assertIsInstance(tenant, Tenant)

    def test_update_oauth_policy_properties(self):
        oauth_policy = self.app.oauth_policy

        oauth_policy.access_token_ttl = 'PT5H'
        oauth_policy.refresh_token_ttl = 'PT10H'
        oauth_policy.save()
        oauth_policy.refresh()

        self.assertEqual(
            oauth_policy.access_token_ttl, datetime.timedelta(hours=5))
        self.assertEqual(
            oauth_policy.refresh_token_ttl, datetime.timedelta(hours=10))

    def test_update_oauth_policy_properties_timedelta(self):
        oauth_policy = self.app.oauth_policy

        oauth_policy.access_token_ttl = datetime.timedelta(hours=5)
        oauth_policy.refresh_token_ttl = datetime.timedelta(hours=10)
        oauth_policy.save()
        oauth_policy.refresh()

        self.assertEqual(
            oauth_policy.access_token_ttl, datetime.timedelta(hours=5))
        self.assertEqual(
            oauth_policy.refresh_token_ttl, datetime.timedelta(hours=10))


class TestSamlApplication(AuthenticatedLiveBase):

    def setUp(self):
        super(TestSamlApplication, self).setUp()

        sso_login_url = 'https://idp.whatever.com/saml2/sso/login'
        sso_logout_url = 'https://idp.whatever.com/saml2/sso/logout'
        encoded_x509_signing_cert = """-----BEGIN CERTIFICATE-----
        MIIDBjCCAe4CCQDkkfBwuV3jqTANBgkqhkiG9w0BAQUFADBFMQswCQYDVQQGEwJV
        UzETMBEGA1UECBMKU29tZS1TdGF0ZTEhMB8GA1UEChMYSW50ZXJuZXQgV2lkZ2l0
        cyBQdHkgTHRkMB4XDTE1MTAxNDIyMDUzOFoXDTE2MTAxMzIyMDUzOFowRTELMAkG
        A1UEBhMCVVMxEzARBgNVBAgTClNvbWUtU3RhdGUxITAfBgNVBAoTGEludGVybmV0
        IFdpZGdpdHMgUHR5IEx0ZDCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEB
        ALuZBSfp4ecigQGFL6zawVi9asVstXHy3cpj3pPXjDx5Xj4QlbBL7KbZhVd4B+j3
        Paacetpn8N0g06sYe1fIeddZE7PZeD2vxTLglriOCB8exH9ZAcYNHIGy3pMFdXHY
        lS7xXYWb+BNLVU7ka3tJnceDjhviAjICzQJs0JXDVQUeYxB80a+WtqJP+ZMbAxvA
        QbPzkcvK8CMctRSRqKkpC4gWSxUAJOqEmyvQVQpaLGrI2zFroD2Bgt0cZzBHN5tG
        wC2qgacDv16qyY+90rYgX/WveA+MSd8QKGLcpPlEzzVJp7Z5Boc3T8wIR29jaDtR
        cK4bWQ2EGLJiJ+Vql5qaOmsCAwEAATANBgkqhkiG9w0BAQUFAAOCAQEAmCND/4tB
        +yVsIZBAQgul/rK1Qj26FlyO0i0Rmm2OhGRhrd9JPQoZ+xCtBixopNICKG7kvUeQ
        Sk8Bku6rQ3VquxKtqAjNFeiLykd9Dn2HUOGpNlRcpzFXHtX+L1f34lMaT54qgWAh
        PgWkzh8xo5HT4M83DaG+HT6BkaVAQwIlJ26S/g3zJ00TrWRP2E6jlhR5KHLN+8eE
        D7/ENlqO5ThU5uX07/Bf+S0q5NK0NPuy0nO2w064kHdIX5/O64ktT1/MgWBV6yV7
        mg1osHToeo4WXGz2Yo6+VFMM3IKRqMDbkR7N4cNKd1KvEKrMaRE7vC14H/G5NSOh
        yl85oFHAdkguTA==
        -----END CERTIFICATE-----
        """

        self.directory = self.client.directories.create(
            {
                'name': self.get_random_name(),
                'description': 'Testing SAML Provider',
                'provider':
                    {
                        'sso_login_url': sso_login_url,
                        'sso_logout_url': sso_logout_url,
                        'encoded_x509_signing_cert': encoded_x509_signing_cert,
                        'request_signature_algorithm':
                            Provider.SIGNING_ALGORITHM_RSA_SHA_256,
                        'provider_id': Provider.SAML
                    },
            })

        self.app = self.client.applications.create(
            {
                'name': self.get_random_name(),
                'description': 'Testing app for SAML Auth',
                'status': 'enabled'
            })

        self.client.account_store_mappings.create(
            {
                'application': self.app,
                'account_store': self.directory,
                'list_index': 0,
                'is_default_account_store': False,
                'is_default_group_store': False
            })

    def tearDown(self):
        self.app.delete()
        self.directory.delete()

    def test_saml_policy_properties(self):
        self.assertIsInstance(self.app.saml_policy, SamlPolicy)
        self.assertIsInstance(
            self.app.saml_policy.service_provider, SamlServiceProvider)
        self.assertIsInstance(
            self.app.saml_policy.service_provider.sso_initiation_endpoint,
            SsoInitiationEndpoint)
        self.assertIsInstance(
            self.app.saml_policy.service_provider.default_relay_states,
            DefaultRelayStateList)
        self.assertIn(
            '/saml/sso/idpRedirect',
            self.app.saml_policy.service_provider.sso_initiation_endpoint.href)

    def test_default_relay_states(self):
        self.app.authorized_callback_uris = [
            'https://myapplication.com/whatever/callback']
        self.app.save()

        name = self.get_random_name()
        name_key = name[:63]
        organization = self.client.tenant.organizations.create({
            'name': name,
            'description': 'test organization',
            'name_key': name_key,
            'status': 'ENABLED'
        })

        drss = self.app.saml_policy.service_provider.default_relay_states
        drs = drss.create()
        self.assertIsInstance(drs, DefaultRelayState)
        self.assertTrue(drs.default_relay_state)
        drs = drss.create(
            {
                'callback_uri': 'https://myapplication.com/whatever/callback',
                'organization': organization,
                'state': 'IAmState',
            })
        self.assertIsInstance(drs, DefaultRelayState)
        self.assertTrue(drs.default_relay_state)

    def test_authorized_callback_uris_append(self):
        self.assertEqual(self.app.authorized_callback_uris, [])
        uri1 = 'https://myapplication.com/whatever/callback1'
        uri2 = 'https://myapplication.com/whatever/callback2'
        uri3 = 'https://myapplication.com/whatever/callback3'
        self.app.authorized_callback_uris = [uri1]
        self.app.save()
        self.app.refresh()

        self.assertEqual(self.app.authorized_callback_uris, [uri1])

        # case when uris are changed elsewhere
        properties = self.app._get_properties()
        properties['authorizedCallbackUris'] = [uri2]
        self.client.data_store.executor.post(self.app.href, properties)

        self.app.authorized_callback_uris.append(uri3)
        self.app.save()
        self.app.refresh()
        self.assertEqual(len(self.app.authorized_callback_uris), 2)
        self.assertEqual(self.app.authorized_callback_uris, [uri2, uri3])

    def test_authorized_callback_uris_extend(self):
        self.assertEqual(self.app.authorized_callback_uris, [])
        uri1 = 'https://myapplication.com/whatever/callback1'
        uri2 = 'https://myapplication.com/whatever/callback2'
        uri3 = 'https://myapplication.com/whatever/callback3'
        uri4 = 'https://myapplication.com/whatever/callback4'
        self.app.authorized_callback_uris = [uri1]
        self.app.save()
        self.app.refresh()

        self.assertEqual(self.app.authorized_callback_uris, [uri1])

        # case when uris are changed elsewhere
        properties = self.app._get_properties()
        properties['authorizedCallbackUris'] = [uri2]
        self.client.data_store.executor.post(self.app.href, properties)

        self.app.authorized_callback_uris.extend([uri3, uri4])
        self.app.save()
        self.app.refresh()
        self.assertEqual(len(self.app.authorized_callback_uris), 3)
        self.assertEqual(self.app.authorized_callback_uris, [uri2, uri3, uri4])

    def test_authorized_callback_uris_insert(self):
        self.assertEqual(self.app.authorized_callback_uris, [])
        uri1 = 'https://myapplication.com/whatever/callback1'
        uri2 = 'https://myapplication.com/whatever/callback2'
        uri3 = 'https://myapplication.com/whatever/callback3'
        uri4 = 'https://myapplication.com/whatever/callback4'
        self.app.authorized_callback_uris = [uri1, uri2]
        self.app.save()
        self.app.refresh()

        self.assertEqual(self.app.authorized_callback_uris, [uri1, uri2])

        # case when uris are changed elsewhere
        properties = self.app._get_properties()
        properties['authorizedCallbackUris'] = [uri2, uri3]
        self.client.data_store.executor.post(self.app.href, properties)

        self.app.authorized_callback_uris.insert(1, uri4)
        self.app.save()
        self.app.refresh()
        self.assertEqual(len(self.app.authorized_callback_uris), 3)
        self.assertEqual(self.app.authorized_callback_uris, [uri2, uri3, uri4])

    def test_authorized_callback_uris_pop(self):
        self.assertEqual(self.app.authorized_callback_uris, [])
        uri1 = 'https://myapplication.com/whatever/callback1'
        uri2 = 'https://myapplication.com/whatever/callback2'
        uri3 = 'https://myapplication.com/whatever/callback3'
        self.app.authorized_callback_uris = [uri1, uri2]
        self.app.save()
        self.app.refresh()

        self.assertEqual(self.app.authorized_callback_uris, [uri1, uri2])

        # case when uris are changed elsewhere
        properties = self.app._get_properties()
        properties['authorizedCallbackUris'] = [uri2, uri3]
        self.client.data_store.executor.post(self.app.href, properties)

        self.app.authorized_callback_uris.pop()
        self.app.save()
        self.app.refresh()
        self.assertEqual(len(self.app.authorized_callback_uris), 1)
        self.assertEqual(self.app.authorized_callback_uris, [uri3])

    def test_authorized_callback_uris_remove(self):
        self.assertEqual(self.app.authorized_callback_uris, [])
        uri1 = 'https://myapplication.com/whatever/callback1'
        uri2 = 'https://myapplication.com/whatever/callback2'
        uri3 = 'https://myapplication.com/whatever/callback3'
        self.app.authorized_callback_uris = [uri1, uri2]
        self.app.save()
        self.app.refresh()

        self.assertEqual(self.app.authorized_callback_uris, [uri1, uri2])

        # case when uris are changed elsewhere
        properties = self.app._get_properties()
        properties['authorizedCallbackUris'] = [uri2, uri3]
        self.client.data_store.executor.post(self.app.href, properties)

        self.app.authorized_callback_uris.remove(uri2)
        self.app.save()
        self.app.refresh()
        self.assertEqual(len(self.app.authorized_callback_uris), 1)
        self.assertEqual(self.app.authorized_callback_uris, [uri3])

        # case when uris are changed elsewhere
        properties = self.app._get_properties()
        properties['authorizedCallbackUris'] = [uri2]
        self.client.data_store.executor.post(self.app.href, properties)

        # try to remove item that doesn't exist any more
        self.app.authorized_callback_uris.remove(uri3)
        self.app.save()
        self.app.refresh()
        self.assertEqual(len(self.app.authorized_callback_uris), 1)
        self.assertEqual(self.app.authorized_callback_uris, [uri2])

        # try to remove item that never existed
        with self.assertRaises(ValueError):
            self.app.authorized_callback_uris.remove(uri3)

    def test_authorized_callback_uris_delete_item(self):
        self.assertEqual(self.app.authorized_callback_uris, [])
        uri1 = 'https://myapplication.com/whatever/callback1'
        uri2 = 'https://myapplication.com/whatever/callback2'
        uri3 = 'https://myapplication.com/whatever/callback3'
        self.app.authorized_callback_uris = [uri1, uri2]
        self.app.save()
        self.app.refresh()

        self.assertEqual(self.app.authorized_callback_uris, [uri1, uri2])

        # case when uris are changed elsewhere
        properties = self.app._get_properties()
        properties['authorizedCallbackUris'] = [uri2, uri3]
        self.client.data_store.executor.post(self.app.href, properties)

        del self.app.authorized_callback_uris[1]
        self.app.save()
        self.app.refresh()
        self.assertEqual(len(self.app.authorized_callback_uris), 1)
        self.assertEqual(self.app.authorized_callback_uris, [uri3])

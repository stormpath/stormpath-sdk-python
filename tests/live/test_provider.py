""""
Integration tests for various pieces involved in external provider support.
"""

from json import loads
from os import getenv

from requests import Session

from tests.live.base import AuthenticatedLiveBase
from stormpath.error import Error as StormpathError
from stormpath.resources import (
    AssertionConsumerServicePostEndpoint,
    AttributeStatementMappingRule,
    AttributeStatementMappingRules,
    Provider,
    SamlServiceProviderMetadata,
)


class TestProviderDirectories(AuthenticatedLiveBase):

    def test_creating_provider_directory_passes_provider_info(self):
        directory = self.client.directories.create({
            'name': self.get_random_name(),
            'description': 'Testing Google Auth Provider',
            'provider': {
                'client_id': 'some-client-id',
                'client_secret': 'some-client-secret',
                'redirect_uri': 'some-redirect-uri',
                'provider_id': Provider.GOOGLE
            }
        })

        app = self.client.applications.create({
            'name': self.get_random_name(),
            'description': 'Testing app for Google Auth',
            'status': 'enabled'
        })

        self.client.account_store_mappings.create({
            'application': app,
            'account_store': directory,
            'list_index': 0,
            'is_default_account_store': False,
            'is_default_group_store': False
        })

        with self.assertRaises(StormpathError) as se:
            app.get_provider_account(provider=Provider.GOOGLE, code='some-code')

        self.assertTrue("Google error message: 400 Bad Request" in str(se.exception.developer_message))

        directory.delete()
        app.delete()

    def test_get_provider_account_makes_request_to_facebook(self):
        facebook_api_key_id = getenv('FACEBOOK_API_KEY_ID')
        facebook_api_key_secret = getenv('FACEBOOK_API_KEY_SECRET')

        if not facebook_api_key_id:
            self.fail('Please set FACEBOOK_API_KEY_ID environment variable!')

        if not facebook_api_key_secret:
            self.fail('Please set FACEBOOK_API_KEY_SECRET environment variable!')

        s = Session()
        res = s.request('GET', 'https://graph.facebook.com/oauth/access_token', params={
            'client_id': facebook_api_key_id,
            'client_secret': facebook_api_key_secret,
            'grant_type': 'client_credentials'
        })
        access_token = res.text.split('=')[1]

        res = s.request('GET', 'https://graph.facebook.com/{}/accounts/test-users'.format(facebook_api_key_id), params={
            'installed': 'true',
            'name': 'Some User',
            'locale': 'en_US',
            'permissions': 'read_stream',
            'method': 'post',
            'access_token': access_token,
        })
        access_token = loads(res.text)['access_token']

        directory = self.client.directories.create({
            'name': self.get_random_name(),
            'description': 'Testing Facebook Auth Provider',
            'provider': {
                'client_id': facebook_api_key_id,
                'client_secret': facebook_api_key_secret,
                'provider_id': Provider.FACEBOOK
            }
        })

        app = self.client.applications.create({
            'name': self.get_random_name(),
            'description': 'Testing app for Facebook Auth',
            'status': 'enabled'
        })

        self.client.account_store_mappings.create({
            'application': app,
            'account_store': directory,
            'list_index': 0,
            'is_default_account_store': False,
            'is_default_group_store': False
        })

        account = app.get_provider_account(provider=Provider.FACEBOOK, access_token=access_token)
        self.assertTrue(account)

        directory.delete()
        app.delete()

    def test_get_provider_account_makes_request_to_github(self):
        github_api_key_id = 'some-api-key-id'
        github_api_key_secret = 'some-api-secret'

        directory = self.client.directories.create({
            'name': self.get_random_name(),
            'description': 'Testing Github Auth Provider',
            'provider': {
                'client_id': github_api_key_id,
                'client_secret': github_api_key_secret,
                'provider_id': Provider.GITHUB
            }
        })

        app = self.client.applications.create({
            'name': self.get_random_name(),
            'description': 'Testing app for Github Auth',
            'status': 'enabled'
        })

        self.client.account_store_mappings.create({
            'application': app,
            'account_store': directory,
            'list_index': 0,
            'is_default_account_store': False,
            'is_default_group_store': False
        })

        with self.assertRaises(StormpathError) as se:
            app.get_provider_account(provider=Provider.GITHUB, access_token='some-access-token')

        self.assertTrue("Github error message: 401 Unauthorized" in str(se.exception.developer_message))

        directory.delete()
        app.delete()

    def test_get_provider_account_makes_request_to_linkedin(self):
        linkedin_api_key_id = 'some-api-key-id'
        linkedin_api_key_secret = 'some-api-key-secret'

        directory = self.client.directories.create({
            'name': self.get_random_name(),
            'description': 'Testing LinkedIn Auth Provider',
            'provider': {
                'client_id': linkedin_api_key_id,
                'client_secret': linkedin_api_key_secret,
                'provider_id': Provider.LINKEDIN
            }
        })

        app = self.client.applications.create({
            'name': self.get_random_name(),
            'description': 'Testing app for LinkedIn Auth',
            'status': 'enabled'
        })

        self.client.account_store_mappings.create({
            'application': app,
            'account_store': directory,
            'list_index': 0,
            'is_default_account_store': False,
            'is_default_group_store': False
        })

        with self.assertRaises(StormpathError) as se:
            app.get_provider_account(provider=Provider.LINKEDIN, access_token='some-access-token')

        self.assertTrue('Linkedin error message: Invalid access token.' in str(se.exception.developer_message))

        directory.delete()
        app.delete()

    def test_create_directory_with_saml_provider(self):
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

        directory = self.client.directories.create({
            'name': self.get_random_name(),
            'description': 'Testing SAML Provider',
            'provider': {
                'sso_login_url': sso_login_url,
                'sso_logout_url': sso_logout_url,
                'encoded_x509_signing_cert': encoded_x509_signing_cert,
                'request_signature_algorithm': Provider.SIGNING_ALGORITHM_RSA_SHA_256,
                'provider_id': Provider.SAML
            }
        })

        self.assertIsNotNone(directory.href)

        provider = directory.provider
        spm = provider.service_provider_metadata
        self.assertIsNotNone(spm.href)
        self.assertIsInstance(spm, SamlServiceProviderMetadata)
        self.assertIsInstance( spm.assertion_consumer_service_post_endpoint, AssertionConsumerServicePostEndpoint)
        self.assertEqual(provider.provider_id, Provider.SAML)
        self.assertEqual(provider.sso_login_url, sso_login_url)
        self.assertEqual(provider.sso_logout_url, sso_logout_url)

        directory.delete()

    def test_create_directory_with_saml_provider_with_asm_rules(self):
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

        directory = self.client.directories.create({
            'name': self.get_random_name(),
            'description': 'Testing SAML Provider',
            'provider': {
                'sso_login_url': sso_login_url,
                'sso_logout_url': sso_logout_url,
                'encoded_x509_signing_cert': encoded_x509_signing_cert,
                'request_signature_algorithm': Provider.SIGNING_ALGORITHM_RSA_SHA_256,
                'provider_id': Provider.SAML
            },
        })

        name_format = 'urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified'
        rule1 = AttributeStatementMappingRule(name='name1', name_format=name_format, account_attributes=['customData.name1', 'customData.otherName1'])
        rule2 = AttributeStatementMappingRule(name='name2', name_format=name_format, account_attributes=['customData.name2'])

        asmr = directory.provider.attribute_statement_mapping_rules
        asmr.items = [rule1]
        asmr.save()

        self.assertIsInstance(asmr, AttributeStatementMappingRules)
        self.assertEqual(len(asmr.items), 1)
        self.assertEqual(asmr.items[0].name, 'name1')

        # case when rules are changed elsewhere
        properties = asmr._get_properties()
        properties['items'] = []
        self.client.data_store.executor.post(asmr.href, properties)

        self.assertEqual(len(asmr.items), 1)
        self.assertEqual(asmr.items[0].name, 'name1')

        items = asmr.items
        items.append(rule2)
        asmr.save()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].name, 'name2')

        directory.delete()

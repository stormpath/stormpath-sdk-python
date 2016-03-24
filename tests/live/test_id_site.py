"""Live tests for IDSite functionality."""


from .base import AuthenticatedLiveBase
from stormpath.resources.id_site import IDSite, IDSiteList
from stormpath.resources.tenant import Tenant


class TestIDSite(AuthenticatedLiveBase):

    def test_id_site_collection_contains_single_idsite(self):
        self.assertEqual(len(self.client.tenant.id_sites), 1)

    def test_id_site_is_id_site_resource(self):
        self.assertIsInstance(self.client.tenant.id_sites, IDSiteList)
        self.assertIsInstance(self.client.tenant.id_sites[0], IDSite)

    def test_id_site_attributes_can_be_written(self):
        id_site = self.client.tenant.id_sites[0]

        id_site.key = 'hi'
        id_site.domain_name = 'test.hi.com'
        id_site.tls_public_cert = 'hi'
        id_site.tls_private_key = 'hi'
        id_site.git_repo_url = 'https://github.com/stormpath/stormpath-sdk-python.git'
        id_site.git_branch = 'master'
        id_site.authorized_origin_urls = ['https://hi.com']
        id_site.authorized_redirect_urls = ['https://hi.com']
        id_site.logo_url = 'https://hi.com/woot.jpg'
        id_site.session_tti = 'P1D'
        id_site.session_ttl = 'P1D'
        id_site.session_cookie_persistent = True

        id_site.save()

        self.assertEqual(id_site.key, 'hi')
        self.assertEqual(id_site.domain_name, 'test.hi.com')
        self.assertEqual(id_site.tls_public_cert, 'hi')
        self.assertEqual(id_site.tls_private_key, 'hi')
        self.assertEqual(id_site.git_repo_url, 'https://github.com/stormpath/stormpath-sdk-python.git')
        self.assertEqual(id_site.git_branch, 'master')
        self.assertEqual(id_site.authorized_origin_urls, ['https://hi.com'])
        self.assertEqual(id_site.authorized_redirect_urls, ['https://hi.com'])
        self.assertEqual(id_site.logo_url, 'https://hi.com/woot.jpg')
        self.assertEqual(id_site.session_tti, 'P1D')
        self.assertEqual(id_site.session_ttl, 'P1D')
        self.assertEqual(id_site.session_cookie_persistent, True)

    def test_id_site_tenant(self):
        id_site = self.client.tenant.id_sites[0]
        self.assertIsInstance(id_site.tenant, Tenant)

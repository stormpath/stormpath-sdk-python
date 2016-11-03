"""Live tests of Client functionality."""


from .base import AuthenticatedLiveBase, LiveBase

from stormpath.cache.null_cache_store import NullCacheStore
from stormpath.client import Client
from stormpath.error import Error


class TestClientInitialization(LiveBase):
    """Assert that Client initialization works as expected."""

    def test_base_url(self):
        client = Client(id=self.api_key_id, secret=self.api_key_secret)
        self.assertEqual(client.BASE_URL, 'https://api.stormpath.com/v1')

        client = Client(id=self.api_key_id, secret=self.api_key_secret, base_url='https://example.com')
        self.assertEqual(client.BASE_URL, 'https://example.com')

    def test_cache_options(self):
        client = Client(
            id = self.api_key_id,
            secret = self.api_key_secret,
            cache_options = {
                'regions': {
                    'customData': {
                        'store': NullCacheStore
                    }
                }
            }
        )

        self.assertIsInstance(client.data_store.cache_manager.caches['customData'].store, NullCacheStore)

    def test_basic_authentication(self):
        client = Client(id=self.api_key_id, secret=self.api_key_secret, scheme='basic')
        list(client.applications)

        api_key = {
            'api_key_id': self.api_key_id,
            'api_key_secret': self.api_key_secret
        }
        client = Client(api_key=api_key, scheme='basic')
        list(client.applications)

        client = Client(api_key_id=self.api_key_id, api_key_secret=self.api_key_secret, scheme='basic')
        list(client.applications)

        client = Client(id=self.api_key_id + 'x', secret=self.api_key_secret + 'x', scheme='basic')
        with self.assertRaises(Error):
            list(client.applications)

    def test_digest_authentication(self):
        client = Client(id=self.api_key_id, secret=self.api_key_secret, scheme='SAuthc1')
        list(client.applications)

        client = Client(id=self.api_key_id + 'x', secret=self.api_key_secret + 'x', scheme='SAuthc1')
        with self.assertRaises(Error):
            list(client.applications)

    def test_environment_variable_authentication(self):
        client = Client()
        list(client.applications)


class TestClientProperties(AuthenticatedLiveBase):
    """Assert all Client properties work as expected."""

    # Maximum amount of resources to create when testing.
    TO_CREATE = 10

    def test_account_store_mappings(self):
        with self.assertRaises(ValueError):
            for asm in self.client.account_store_mappings:
                pass

        app = self.client.applications.create({'name': self.get_random_name()})
        dir = self.client.directories.create({'name': self.get_random_name()})
        asm = self.client.account_store_mappings.create({
            'application': app,
            'account_store': dir,
        })

        fasm = self.client.account_store_mappings.get(asm.href)
        self.assertEqual(fasm.href, asm.href)

    def test_accounts(self):
        num_accs = len(self.client.accounts)

        dir = self.client.directories.create({'name': self.get_random_name()})
        self.assertEqual(len(self.client.accounts), num_accs)

        acc = dir.accounts.create({
            'given_name': 'Randall',
            'surname': 'Degges',
            'email': '{}@testmail.stormpath.com'.format(self.get_random_name()),
            'password': 'wootILOVEc00kies!!<33',
        })
        self.assertEqual(len(self.client.accounts), num_accs + 1)

        acc.delete()
        self.assertEqual(len(self.client.accounts), num_accs)

        for i in range(self.TO_CREATE):
            acc = dir.accounts.create({
                'given_name': 'Randall',
                'surname': 'Degges',
                'email': '{}@testmail.stormpath.com'.format(self.get_random_name()),
                'password': 'wootILOVEc00kies!!<33',
            })

        self.assertEqual(len(self.client.accounts), num_accs + self.TO_CREATE)

        facc = self.client.accounts.get(acc.href)
        self.assertEqual(facc.href, acc.href)

    def test_agents(self):
        num_agents = len(self.client.agents)

        for i in range(self.TO_CREATE):
            dir = self.client.directories.create({
                'name': self.get_random_name(),
                'provider': {
                    'provider_id': 'ldap',
                    'agent': {
                        'status': 'offline',
                        'config': {
                            'directory_host': 'xxx',
                            'directory_port': 31337,
                            'ssl_required': True,
                            'agent_user_dn': 'xxx',
                            'agent_user_dn_password': 'xxx',
                            'base_dn': 'xxx',
                            'poll_interval': 1,
                            'account_config': {
                                'dn_suffix': 'xxx',
                                'object_class': 'xxx',
                                'object_filter': 'xxx',
                                'email_rdn': 'xxx',
                                'given_name_rdn': 'xxx',
                                'middle_name_rdn': 'xxx',
                                'surname_rdn': 'xxx',
                                'username_rdn': 'xxx',
                                'password_rdn': 'xxx',
                            },
                            'group_config': {
                                'dn_suffix': 'xxx',
                                'object_class': 'xxx',
                                'object_filter': 'xxx',
                                'name_rdn': 'xxx',
                                'description_rdn': 'xxx',
                                'members_rdn': 'xxx',
                            }
                        }
                    }
                }
            })
            agent = dir.provider.agent

        self.assertEqual(agent.status, 'OFFLINE')
        self.assertEqual(len(self.client.agents), num_agents + self.TO_CREATE)

        fagent = self.client.agents.get(agent.href)
        self.assertEqual(fagent.href, agent.href)

    def test_api_keys(self):
        with self.assertRaises(ValueError):
            for api_key in self.client.api_keys:
                pass

        app = self.client.applications.create({'name': self.get_random_name()}, create_directory=True)
        account = app.accounts.create({
            'given_name': self.get_random_name(),
            'surname': self.get_random_name(),
            'email': '{}@testmail.stormpath.com'.format(self.get_random_name()),
            'password': 'wootILOVEc00kies!!<33',
        })
        key = account.api_keys.create()

        fkey = self.client.api_keys.get(key.href)
        self.assertEqual(fkey.id, key.id)
        self.assertEqual(fkey.secret, key.secret)

    def test_applications(self):
        num_apps = len(self.client.applications)

        app = self.client.applications.create({'name': self.get_random_name()})
        self.assertEqual(len(self.client.applications), num_apps + 1)

        app.delete()
        self.assertEqual(len(self.client.applications), num_apps)

        for i in range(self.TO_CREATE):
            app = self.client.applications.create({'name': self.get_random_name()})

        self.assertEqual(len(self.client.applications), num_apps + self.TO_CREATE)

        fapp = self.client.applications.get(app.href)
        self.assertEqual(fapp.href, app.href)

    def test_directories(self):
        num_dirs = len(self.client.directories)

        dir = self.client.directories.create({'name': self.get_random_name()})
        self.assertEqual(len(self.client.directories), num_dirs + 1)

        dir.delete()
        self.assertEqual(len(self.client.directories), num_dirs)

        for i in range(self.TO_CREATE):
            dir = self.client.directories.create({'name': self.get_random_name()})

        self.assertEqual(len(self.client.directories), num_dirs + self.TO_CREATE)

        fdir = self.client.directories.get(dir.href)
        self.assertEqual(fdir.href, dir.href)

    def test_group_memberships(self):
        with self.assertRaises(ValueError):
            for gm in self.client.group_memberships:
                pass

        dir = self.client.directories.create({'name': self.get_random_name()})
        group = dir.groups.create({'name': self.get_random_name()})
        account = dir.accounts.create({
            'given_name': self.get_random_name(),
            'surname': self.get_random_name(),
            'email': '{}@testmail.stormpath.com'.format(self.get_random_name()),
            'password': 'wootILOVEc00kies!!<33',
        })
        gm = self.client.group_memberships.create({
            'account': account,
            'group': group,
        })

        fgm = self.client.group_memberships.get(gm.href)
        self.assertEqual(fgm.href, gm.href)

    def test_groups(self):
        num_groups = len(self.client.groups)

        app = self.client.applications.create({'name': self.get_random_name()}, create_directory=True)
        self.assertEqual(len(self.client.groups), num_groups)

        group = app.groups.create({'name': self.get_random_name()})
        self.assertEqual(len(self.client.groups), num_groups + 1)

        group.delete()
        self.assertEqual(len(self.client.groups), num_groups)

        for i in range(self.TO_CREATE):
            group = app.groups.create({'name': self.get_random_name()})

        self.assertEqual(len(self.client.groups), num_groups + self.TO_CREATE)

        fgroup = self.client.groups.get(group.href)
        self.assertEqual(fgroup.href, group.href)

    def test_id_sites(self):
        self.assertEqual(len(self.client.id_sites), 1)

        id_site = self.client.id_sites[0]
        fid_site = self.client.id_sites.get(id_site.href)

        self.assertEqual(fid_site.href, id_site.href)

    def test_organization_account_store_mappings(self):
        with self.assertRaises(ValueError):
            for oasm in self.client.organization_account_store_mappings:
                pass

        org = self.client.organizations.create({
            'name': self.get_random_name(),
            'name_key': self.get_random_name()[:63],
        })
        dir = self.client.directories.create({'name': self.get_random_name()})
        oasm = self.client.organization_account_store_mappings.create({
            'organization': org,
            'account_store': dir,
        })

        foasm = self.client.organization_account_store_mappings.get(oasm.href)
        self.assertEqual(foasm.href, oasm.href)

    def test_organizations(self):
        num_orgs = len(self.client.organizations)

        org = self.client.organizations.create({
            'name': self.get_random_name(),
            'name_key': self.get_random_name()[:63],
        })
        self.assertEqual(len(self.client.organizations), num_orgs + 1)

        org.delete()
        self.assertEqual(len(self.client.organizations), num_orgs)

        for i in range(self.TO_CREATE):
            org = self.client.organizations.create({
                'name': self.get_random_name(),
                'name_key': self.get_random_name()[:63],
            })

        self.assertEqual(len(self.client.organizations), num_orgs + self.TO_CREATE)

        forg = self.client.organizations.get(org.href)
        self.assertEqual(forg.href, org.href)

"""Live tests of Mirror Directories and Agent functionality."""

from .base import AuthenticatedLiveBase
from stormpath.resources.agent import AgentConfig, AgentDownload


class TestMirrorDirectoryAgent(AuthenticatedLiveBase):

    def setUp(self):
        super(TestMirrorDirectoryAgent, self).setUp()

        self.name = self.get_random_name()

        self.ad_directory = self.client.directories.create({
            'name': self.name,
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

        self.ad_agent = self.ad_directory.provider.agent

    def test_get_agent_from_agents(self):
        agent = self.client.agents.get(self.ad_agent.href)

        self.assertEqual(agent.status, 'OFFLINE')
        self.assertIsInstance(agent.config, AgentConfig)
        self.assertIsInstance(agent.download, AgentDownload)

    def test_update_agent(self):
        self.ad_agent.config.ssl_required = False
        self.ad_agent.config.account_config.email_rdn = 'electronic-mail'
        self.ad_agent.config.group_config.name_rdn = 'name'
        self.ad_agent.save()

        agent = self.client.agents.get(self.ad_agent.href)
        self.assertFalse(agent.config.ssl_required)
        self.assertEqual(
            agent.config.account_config.email_rdn, 'electronic-mail')
        self.assertEqual(agent.config.group_config.name_rdn, 'name')

    def test_get_agents_from_tenant(self):
        self.assertTrue(
            self.ad_agent.href in [a.href for a in self.client.tenant.agents])

    def test_create_agent(self):
        with self.assertRaises(ValueError):
            self.client.agents.create('whatever')

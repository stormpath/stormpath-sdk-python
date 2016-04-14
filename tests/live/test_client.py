"""Live tests of Client functionality."""


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


class TestClientProperties(AuthenticatedLiveBase):
    """Assert all Client properties work as expected."""

    def test_client_api_keys(self):
        self.assertEqual(len(self.client.api_keys), 1)

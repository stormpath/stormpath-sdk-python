"""Stormpath API client."""


from .auth import Auth
from .data_store import DataStore
from .http import HttpExecutor
from .resources.account import AccountList
from .resources.account_store_mapping import AccountStoreMappingList
from .resources.agent import AgentList
from .resources.group import GroupList
from .resources.group_membership import GroupMembershipList
from .resources.tenant import Tenant


class Client(object):
    """The root entry point for SDK functionality.

    Using the client instance, you can access all tenant data, such as
    applications, directories, groups, and accounts.

    More info in documentation:
    http://docs.stormpath.com/python/product-guide/#sdk-concepts

    The client contains the following attributes that represent resource lists:

    :py:attr:`applications` -
    :class:`stormpath.resources.application.ApplicationList`

    :py:attr:`directories` -
    :class:`stormpath.resources.directory.DirectoryList`

    :py:attr:`accounts` -
    :class:`stormpath.resources.account.AccountList`

    :py:attr:`groups` -
    :class:`stormpath.resources.group.GroupList`

    :py:attr:`group_memberships` -
    :class:`stormpath.resources.group_membership.GroupMembershipList`

    :py:attr:`account_store_mappings` -
    :class:`stormpath.resources.account_store_mapping.AccountStoreMappingList`
    """
    BASE_URL = 'https://api.stormpath.com/v1'

    def __init__(self, base_url=None, cache_options=None, expand=None, proxies=None, user_agent=None, backoff_strategy=None, **auth_kwargs):
        """
        Initialize the client by setting the
        :class:`stormpath.data_store.DataStore` and
        :class:`stormpath.resources.tenant.Tenant`.

        The parameters the Client accepts are those used by the
        :class:`stormpath.http.HttpExecutor`, :class:`stormpath.auth.Auth`, and
        :class:`stormpath.data_store.DataStore` classes.

        :param str user_agent: (optional) The custom user agent to set.

        :param backoff_strategy: A Function that will return the number of milliseconds
            to wait before retrying the request. The function must take one parameter
            which is the number of retries already done. If no function is supplied
            the default backoff strategy is used (see the :meth:`stormpath.http.HttpExecutor.pause_exponentially` method).
        """
        self.BASE_URL = base_url or self.BASE_URL

        self.auth = Auth(**auth_kwargs)
        executor = HttpExecutor(self.BASE_URL, self.auth.scheme, proxies, user_agent=user_agent, get_delay=backoff_strategy)
        self.data_store = DataStore(executor, cache_options)
        self.tenant = Tenant(client=self, href='/tenants/current', expand=expand)

    @property
    def applications(self):
        return self.tenant.applications

    @property
    def directories(self):
        return self.tenant.directories

    @property
    def accounts(self):
        return AccountList(self, href='/accounts')

    @property
    def groups(self):
        return GroupList(self, href='/groups')

    @property
    def group_memberships(self):
        return GroupMembershipList(self, href='/groupMemberships')

    @property
    def account_store_mappings(self):
        return AccountStoreMappingList(self, href='/accountStoreMappings')

    @property
    def agents(self):
        return AgentList(self, href='/agents')

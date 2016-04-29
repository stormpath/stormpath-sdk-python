"""Stormpath API client."""


from .auth import Auth
from .data_store import DataStore
from .http import HttpExecutor
from .resources.account_store_mapping import AccountStoreMappingList
from .resources.api_key import ApiKeyList
from .resources.group_membership import GroupMembershipList
from .resources.organization_account_store_mapping import OrganizationAccountStoreMappingList
from .resources.tenant import Tenant


class Client(object):
    """The Client object is what handles all connections to Stormpath, and is
    the entry point for all Stormpath usage.

    Using the Client instance, you can access all Tenant data, such as
    Applications, Directories, Organizations, Groups, and Accounts.

    More info can be found in our documentation:
    http://docs.stormpath.com/python/product-guide/#sdk-concepts

    Examples::

        client = Client(id='xxx', secret='xxx')
        client = Client(id='xxx', secret='xxx', base_url='https://enterprise.stormpath.io/v1')
        client = Client(api_key_id='xxx', api_key_secret='xxx')
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
    def account_store_mappings(self):
        """
        This property allows you to access AccountStoreMapping resources.

        .. note::
            You *cannot* iterate over AccountStoreMappings directly from this
            Client object.  This is not supported by the Stormpath API.

        Examples:

        Creating an AccountStoreMapping::

            mapping = client.account_store_mappings.create({
                'application': application,
                'account_store': account_store,
            })

        Fetching an existing AccountStoreMapping::

            mapping = client.account_store_mappings.get(href)
        """
        return AccountStoreMappingList(self, href='/accountStoreMappings')

    @property
    def accounts(self):
        """
        This property allows you to access Account resources.

        .. note::
            You *cannot* create Accounts directly from this Client object.  This
            is not supported by the Stormpath API.

        Examples:

        Iterate over existing Accounts::

            for account in client.accounts:
                ...

        Fetching an existing Account::

            account = client.accounts.get(href)
        """
        return self.tenant.accounts

    @property
    def agents(self):
        """
        This property allows you to access Agent resources.

        .. note::
            You *cannot* create Agents directly from this Client object.  This
            is not supported by the Stormpath API.

        Examples:

        Iterate over existing Agents::

            for agent in client.agents:
                ...

        Fetching an existing Agent::

            agent = client.agents.get(href)
        """
        return self.tenant.agents

    @property
    def api_keys(self):
        """
        This property allows you to access ApiKey resources.

        .. note::
            You *cannot* create ApiKeys directly from this Client object.  This
            is not supported by the Stormpath API.

            You *cannot* iterate over ApiKeys directly from this Client object.
            This is not supported by the Stormpath API.

        Examples:

        Fetching an existing ApiKey::

            api_key = client.api_keys.get(href)
        """
        return ApiKeyList(self, href='/apiKeys')

    @property
    def applications(self):
        """
        This property allows you to access Application resources.

        Examples:

        Creating an Application::

            application = client.applications.create({'name': 'xxx'})

        Iterate over existing Applications::

            for application in client.applications:
                ...

        Fetching an existing Application::

            application = client.applications.get(href)
        """
        return self.tenant.applications

    @property
    def directories(self):
        """
        This property allows you to access Directory resources.

        Examples:

        Creating an Directory::

            directory = client.directories.create({'name': 'xxx'})

        Iterate over existing Directories::

            for directory in client.directories:
                ...

        Fetching an existing Directory::

            directory = client.directories.get(href)
        """
        return self.tenant.directories

    @property
    def group_memberships(self):
        """
        This property allows you to access GroupMembership resources.

        .. note::
            You *cannot* iterate over GroupMemberships directly from this
            Client object.  This is not supported by the Stormpath API.

        Examples:

        Creating a GroupMembership::

            membership = client.group_memberships.create({
                'account': account,
                'group': group,
            })

        Fetching an existing GroupMembership::

            membership = client.group_memberships.get(href)
        """
        return GroupMembershipList(self, href='/groupMemberships')

    @property
    def groups(self):
        """
        This property allows you to access Group resources.

        .. note::
            You *cannot* create Groups directly from this Client object.  This
            is not supported by the Stormpath API.

        Examples:

        Iterate over existing Groups::

            for group in client.groups:
                ...

        Fetching an existing Group::

            group = client.groups.get(href)
        """
        return self.tenant.groups

    @property
    def id_sites(self):
        """
        This property allows you to access IDSite resources.

        .. note::
            You *cannot* create IDSites directly from this Client object.  This
            is not supported by the Stormpath API.

        Examples:

        Iterate over existing IDSites::

            for id_site in client.id_sites:
                ...

        Fetching an existing IDSite::

            id_site = client.id_sites.get(href)
        """
        return self.tenant.id_sites

    @property
    def organization_account_store_mappings(self):
        """
        This property allows you to access OrganizationAccountStoreMapping resources.

        .. note::
            You *cannot* iterate over OrganizationAccountStoreMappings directly
            from this Client object.  This is not supported by the Stormpath
            API.

        Examples:

        Creating an OrganizationAccountStoreMapping::

            mapping = client.organization_account_store_mappings.create({
                'organization': organization,
                'account_store': account_store,
            })

        Fetching an existing OrganizationAccountStoreMapping::

            mapping = client.organization_account_store_mappings.get(href)
        """
        return OrganizationAccountStoreMappingList(self, href='/organizationAccountStoreMappings')

    @property
    def organizations(self):
        """
        This property allows you to access Organization resources.

        Examples:

        Creating an Organization::

            organization = client.organizations.create({
                'name': 'xxx',
                'name_key': 'xxx',
            })

        Iterate over existing Organizations::

            for organization in client.organizations:
                ...

        Fetching an existing Organization::

            organization = client.organizations.get(href)
        """
        return self.tenant.organizations

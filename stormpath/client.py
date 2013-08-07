from .auth import Auth
from .http import HttpExecutor
from .data_store import DataStore
from .resource.tenant import Tenant
from .resource.account import AccountList
from .resource.group import GroupList
from .resource.group_membership import GroupMembershipList


class Client(object):
    """ The root entry point for SDK functionality.

    Using the client instance, you can access all tenant data, such as
    applications, directories, groups, and accounts.

    More info in documentation:
    https://www.stormpath.com/docs/python/product-guide#Client
    """

    BASE_URL = 'https://api.stormpath.com/v1'

    def __init__(self, cache_options=None, **kwargs):
        executor = HttpExecutor(self.BASE_URL, Auth(**kwargs).digest)
        self.data_store = DataStore(executor, cache_options)
        self.tenant = Tenant(client=self, href='/tenants/current')

        """
        Initialize the client by setting the
        :class:`stormpath.data_store.DataStore` and
        :class:`stormpath.resource.tenant.Tenant`.
        The parameters the Client accepts are those used by
        :class:`stormpath.http.HttpExecutor` and
        :class:`stormpath.data_store.DataStore` classes.
        """

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

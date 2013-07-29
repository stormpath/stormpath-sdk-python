from .auth import Auth
from .http import HttpExecutor
from .data_store import DataStore
from .resource.tenant import Tenant
from .resource.account import AccountList
from .resource.group import GroupList
from .resource.group_membership import GroupMembershipList


class Client(object):
    BASE_URL = 'https://api.stormpath.com/v1'

    def __init__(self, **kwargs):
        # FIXME - can't use digest yet
        executor = HttpExecutor(self.BASE_URL, Auth(**kwargs).basic)
        self.data_store = DataStore(executor)
        self.tenant = Tenant(client=self, href='/tenants/current')

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

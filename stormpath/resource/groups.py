__author__ = 'ecrisostomo'

from stormpath.resource.resource import CollectionResource, InstanceResource, StatusResource
from stormpath.resource.accounts import AccountList
from stormpath.resource.group_memberships import GroupMembership
from stormpath.resource.directories import Directory
from stormpath.resource.tenants import Tenant

class Group(InstanceResource, StatusResource):

    NAME = "name"
    DESCRIPTION = "description"
    TENANT = "tenant"
    DIRECTORY = "directory"
    ACCOUNTS = "accounts"

    @property
    def name(self):
        return self.get_property(self.NAME)

    @name.setter
    def name(self, name):
        self._set_property_(self.NAME, name)

    @property
    def description(self):
        return self.get_property(self.DESCRIPTION)

    @description.setter
    def description(self, description):
        self._set_property_(self.DESCRIPTION, description)

    @property
    def tenant(self):
        return self._get_resource_property_(self.TENANT, Tenant)

    @property
    def directory(self):
        return self._get_resource_property_(self.DIRECTORY, Directory)

    @property
    def accounts(self):
        return self._get_resource_property_(self.ACCOUNTS, AccountList)

    def add_account(self, account):
        return GroupMembership._create_(account, self, self.data_store)

class GroupList(CollectionResource):
    pass

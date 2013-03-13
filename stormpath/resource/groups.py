__author__ = 'ecrisostomo'

import stormpath
from stormpath.resource.resource import CollectionResource, InstanceResource, StatusResource

class Group(InstanceResource, StatusResource):

    NAME = "name"
    DESCRIPTION = "description"
    TENANT = "tenant"
    DIRECTORY = "directory"
    ACCOUNTS = "accounts"

    @property
    def name(self):
        return self._get_property_(self.NAME)

    @name.setter
    def name(self, name):
        self._set_property_(self.NAME, name)

    @property
    def description(self):
        return self._get_property_(self.DESCRIPTION)

    @description.setter
    def description(self, description):
        self._set_property_(self.DESCRIPTION, description)

    @property
    def tenant(self):
        return self._get_resource_property_(self.TENANT, stormpath.resource.Tenant)

    @property
    def directory(self):
        return self._get_resource_property_(self.DIRECTORY, stormpath.resource.Directory)

    @property
    def accounts(self):
        return self._get_resource_property_(self.ACCOUNTS, stormpath.resource.AccountList)

    def add_account(self, account):
        return stormpath.resource.GroupMembership._create_(account, self, self.data_store)

class GroupList(CollectionResource):

    @property
    def item_type(self):
        return Group

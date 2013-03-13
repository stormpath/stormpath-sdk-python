__author__ = 'ecrisostomo'

import stormpath
from stormpath.resource.resource import InstanceResource, CollectionResource, StatusResource

class Directory(InstanceResource, StatusResource):

    NAME = "name"
    DESCRIPTION = "description"
    ACCOUNTS = "accounts"
    GROUPS = "groups"
    TENANT = "tenant"

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
    def accounts(self):
        return self._get_resource_property_(self.ACCOUNTS, stormpath.resource.AccountList)

    @property
    def groups(self):
        return self._get_resource_property_(self.GROUPS, stormpath.resource.GroupList)

    def create_account(self, account, registration_workflow_enabled = True):
        accounts = self.accounts
        href = accounts.href

        if not registration_workflow_enabled:
            href += '?registrationWorkflowEnabled=' + str(registration_workflow_enabled).lower()

        return self.data_store.create(href, account, stormpath.resource.Account)

    def create_group(self, group):
        groups = self.groups
        href = groups.href
        return self.data_store.create(href, group, stormpath.resource.Group)

class DirectoryList(CollectionResource):

    @property
    def item_type(self):
        return Directory

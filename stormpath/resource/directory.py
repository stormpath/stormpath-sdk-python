#
# Copyright 2012, 2013 Stormpath, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from stormpath.resource.instance import Instance
from stormpath.resource.account import AccountList, Account
from stormpath.resource.base import Collection


class Directory(Instance, Collection):

    NAME = "name"
    DESCRIPTION = "description"
    TENANT = "tenant"
    ACCOUNTS = "accounts"
    PASSWORD_RESET_TOKENS = "passwordResetTokens"

    @property
    def name(self):
        return self._get_property(self.NAME)

    @property
    def description(self):
        return self._get_property(self.DESCRIPTION)

    @property
    def accounts(self):
        return self._get_resource_property(self.ACCOUNTS, AccountList)

    def create_account(self, account, registration_workflow_enabled=None):
        href = self.accounts.href
        if registration_workflow_enabled is not None:
            href = href + "?registrationWorkflowEnabled=" + \
                str(registration_workflow_enabled).lower()

        return self.create(account, "accounts", href, Account)


class DirectoryList(Collection):

    @property
    def item_type(self):
        return Directory

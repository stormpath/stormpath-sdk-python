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
from stormpath.resource.base import Collection
from stormpath.resource.account import AccountList
from stormpath.auth.basic_authenticator import BasicAuthenticator


class Application(Instance):

    NAME = "name"
    DESCRIPTION = "description"
    TENANT = "tenant"
    ACCOUNTS = "accounts"
    PASSWORD_RESET_TOKENS = "passwordResetTokens"

    @property
    def name(self):
        return self._get_property(self.NAME)

    @name.setter
    def name(self, name):
        self._set_property(self.NAME, name)

    @property
    def description(self):
        return self._get_property(self.DESCRIPTION)

    @description.setter
    def description(self, description):
        self._set_property(self.NAME, description)

    @property
    def accounts(self):
        return self._get_resource_property_(self.ACCOUNTS, AccountList)

    def authenticate_account(self, request):
        """
        Authenticates an account's submitted principals and credentials
        (e.g. username and password).  The account must be in one of the
        Application's "assigned Login Sources":
            http://www.stormpath.com/docs/managing-applications-login-sources.
        If not in an assigned login source, the attempt will fail.
        -Example
        Consider the following username/password-based example:

            request = UsernamePasswordRequest(username, PlaintextPassword, None)
            account = appToTest.authenticate_account(request).get_account

        :param UsernamePasswordRequest request: the authentication request
        representing an account's principals and credentials (e.g.
                       username/password) used to verify their identity.
        :returns the result of the authentication.
        The authenticated account can be obtained from code result.

        :raises ResourceError if the authentication attempt fails.
        """
        response = BasicAuthenticator(self.data_store)
        return response.authenticate(self.href, request)


class ApplicationList(Collection):

    @property
    def item_type(self):
        return Application

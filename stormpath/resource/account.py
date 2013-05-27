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


class Account(Instance):
    USERNAME = "username"
    EMAIL = "email"
    PASSWORD = "password"
    GIVEN_NAME = "givenName"
    MIDDLE_NAME = "middleName"
    SURNAME = "surname"
    GROUPS = "groups"
    DIRECTORY = "directory"
    EMAIL_VERIFICATION_TOKEN = "emailVerificationToken"
    GROUP_MEMBERSHIPS = "groupMemberships"

    @property
    def username(self):
        return self._get_property(self.USERNAME)

    @username.setter
    def username(self, username):
        self._set_property(self.USERNAME, username)

    @property
    def email(self):
        return self._get_property(self.EMAIL)

    @email.setter
    def email(self, email):
        self._set_property(self.EMAIL, email)

    @property
    def password(self):
        #password should never be revealed,
        #but this method is needed to have the setter
        return None

    @password.setter
    def password(self, password):
        self._set_property(self.PASSWORD, password)

    @property
    def given_name(self):
        return self._get_property(self.GIVEN_NAME)

    @given_name.setter
    def given_name(self, given_name):
        self._set_property(self.GIVEN_NAME, given_name)

    @property
    def middle_name(self):
        return self._get_property(self.MIDDLE_NAME)

    @middle_name.setter
    def middle_name(self, middle_name):
        self._set_property(self.MIDDLE_NAME, middle_name)

    @property
    def surname(self):
        return self._get_property(self.SURNAME)

    @surname.setter
    def surname(self, surname):
        self._set_property(self.SURNAME, surname)


class AccountList(Collection):

    @property
    def item_type(self):
        return Account

    def create(self, properties_or_resource, property_name=None, href=None):
        property_name = property_name or "accounts"
        super(AccountList, self).create(
            properties_or_resource, property_name, href)

__author__ = 'ecrisostomo'

import stormpath
from stormpath.resource.resource import InstanceResource, CollectionResource, StatusResource

class Account(InstanceResource, StatusResource):

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
        return self._get_property_(self.USERNAME)

    @username.setter
    def username(self, username):
        self._set_property_(self.USERNAME, username)

    @property
    def email(self):
        return self._get_property_(self.EMAIL)

    @email.setter
    def email(self, email):
        self._set_property_(self.EMAIL, email)

    @property
    def password(self):
        return None #password should never be revealed, but this method is needed to have the setter

    @password.setter
    def password(self, password):
        self._set_property_(self.PASSWORD, password)

    @property
    def given_name(self):
        return self._get_property_(self.GIVEN_NAME)

    @given_name.setter
    def given_name(self, given_name):
        self._set_property_(self.GIVEN_NAME, given_name)

    @property
    def middle_name(self):
        return self._get_property_(self.MIDDLE_NAME)

    @middle_name.setter
    def middle_name(self, middle_name):
        self._set_property_(self.MIDDLE_NAME, middle_name)

    @property
    def surname(self):
        return self._get_property_(self.SURNAME)

    @surname.setter
    def surname(self, surname):
        self._set_property_(self.SURNAME, surname)

    @property
    def groups(self):
        return self._get_resource_property_(self.GROUPS, stormpath.resource.GroupList)

    @property
    def directory(self):
        return self._get_resource_property_(self.DIRECTORY, stormpath.resource.Directory)

    @property
    def email_verification_token(self):
        return self._get_resource_property_(self.EMAIL_VERIFICATION_TOKEN, stormpath.resource.EmailVerificationToken)

    @property
    def group_memberships(self):
        return self._get_resource_property_(self.GROUP_MEMBERSHIPS, stormpath.resource.GroupMembershipList)

    def add_group(self, group):
        return stormpath.resource.GroupMembership._create_(self, group, self.data_store)

class AccountList(CollectionResource):

    @property
    def item_type(self):
        return Account

__author__ = 'ecrisostomo'

from stormpath.resource.accounts import *
from stormpath.resource.resource import Resource

class PasswordResetToken(Resource):

    EMAIL = "email"
    ACCOUNT = "account"

    @property
    def email(self):
        return self.get_property(self.EMAIL)

    @email.setter
    def email(self, email):
        self._set_property_(self.EMAIL, email)

    @property
    def account(self):
        return self._get_resource_property_(self.ACCOUNT, Account)

__author__ = 'ecrisostomo'

import stormpath
from stormpath.resource.resource import Resource

class PasswordResetToken(Resource):

    EMAIL = "email"
    ACCOUNT = "account"

    @property
    def email(self):
        return self._get_property_(self.EMAIL)

    @email.setter
    def email(self, email):
        self._set_property_(self.EMAIL, email)

    @property
    def account(self):
        return self._get_resource_property_(self.ACCOUNT, stormpath.resource.Account)

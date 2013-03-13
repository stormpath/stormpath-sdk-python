__author__ = 'ecrisostomo'

import stormpath

from stormpath.resource.resource import Resource

class UsernamePasswordRequest:

    def __init__(self, username, password, host = None):
        self.principals = username
        self.credentials = password
        self.host = host

    def clear(self):
        """
        Clears out (None) the username, password, and host.  The password bytes are explicitly set to
        0x00 to eliminate the possibility of memory access at a later time.
        """
        self.principals = None
        self.host = None

        for c in self.credentials:
            c = 0x00

        self.credentials = None

class AuthenticationResult(Resource):

    ACCOUNT = "account"

    @property
    def account(self):
        return self._get_resource_property_(self.ACCOUNT, stormpath.resource.Account)

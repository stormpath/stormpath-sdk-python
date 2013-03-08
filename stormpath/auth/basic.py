__author__ = 'ecrisostomo'

import base64
import stormpath

from stormpath.auth.request_result import AuthenticationResult, UsernamePasswordRequest
from stormpath.util import assert_instance, assert_not_none
from stormpath.resource.resource import Resource

class BasicLoginAttempt(Resource):

    TYPE = "type"
    VALUE = "value"

    def type(self):
        return self.get_property(self.TYPE)

    def type(self, type):
        self._set_property_(self.TYPE, type)

    def value(self):
        return self.get_property(self.VALUE)

    def value(self, value):
        self._set_property_(self.VALUE, value)

class BasicAuthenticator:

    def __init__(self, data_store):
        assert_instance(data_store, stormpath.ds.data_store.DataStore, 'data_store')
        self.data_store = data_store

    def authenticate(self, parent_href, request):
        assert_not_none(parent_href, "parent_href must be specified.")
        assert_instance(request, UsernamePasswordRequest, 'request')

        username = request.principals if request.principals else ''
        password = request.credentials if request.credentials else ''

        value = base64.b64encode(bytes((username + ':' + password).encode()))

        attempt = self.data_store.instantiate(BasicLoginAttempt)
        attempt.type('basic')
        attempt.value(value.decode())

        href = parent_href + '/loginAttempts'

        return self.data_store.create(href, attempt, AuthenticationResult)



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

import base64

from stormpath.data_store import DataStore
from stormpath.util import assert_instance, assert_not_none
from stormpath.auth.username_password_request import UsernamePasswordRequest
from stormpath.auth.authentication_result import AuthenticationResult
from stormpath.auth.basic_login_attempt import BasicLoginAttempt


class BasicAuthenticator(object):

    def __init__(self, data_store):
        assert_instance(data_store, DataStore, 'data_store')
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

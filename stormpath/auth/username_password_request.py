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


class UsernamePasswordRequest(object):

    def __init__(self, username, password, host=None):
        self.principals = username
        self.credentials = password
        self.host = host

    def clear(self):
        """
        Clears out (None) the username, password, and host.
        The password bytes are explicitly set to 0x00
        to eliminate the possibility of memory access at a later time.
        """
        self.principals = None
        self.host = None

        for c in self.credentials:
            c = 0x00

        self.credentials = None

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


class Error(RuntimeError):

    def __init__(self, error):
        super().__init__(error.message if error else None)
        self.error = error

    @property
    def status(self):
        return self.error.status if self.error else -1

    @property
    def code(self):
        return self.error.code if self.error else -1

    @property
    def developer_message(self):
        return self.error.developer_message if self.error else None

    @property
    def more_info(self):
        return self.error.more_info if self.error else None

    @property
    def message(self):
        return self.error.message if self.error else None

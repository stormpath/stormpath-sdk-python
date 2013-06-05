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

from stormpath.resource.base import Base


class ResourceError(Base):

    STATUS = "status"
    CODE = "code"
    MESSAGE = "message"
    DEV_MESSAGE = "developerMessage"
    MORE_INFO = "moreInfo"

    def __init__(self, properties):
        super(ResourceError, self).__init__(properties_or_url=properties)

    @property
    def status(self):
        return self._get_property(self.STATUS)

    @property
    def code(self):
        return self._get_property(self.CODE)

    @property
    def message(self):
        return self._get_property(self.MESSAGE)

    @property
    def developer_message(self):
        return self._get_property(self.DEV_MESSAGE)

    @property
    def more_info(self):
        return self._get_property(self.MORE_INFO)

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
#

from stormpath.resource.instance import Instance
from stormpath.resource.application import ApplicationList
from stormpath.resource.directory import DirectoryList


class Tenant(Instance):
    """
    Description
        When you initially sign up for Stormpath, three resources are
        automatically established:
        a default application and directory and a user account known as the Tenant owner,
        which represents the first person that signed up for Stormpath.

    Default Usage
        The Tenant can be used to access the href and name.
        E.g.

        client = Client(api_key={'id': id, 'secret': secret})
        tenant_href = client.tenant.href
        tenant_name = client.tenant.name

        It can also be used to access applications and directories.
        E.g.

        client = Client(api_key={'id': id, 'secret': secret})
        applications = client.tenant.applications
        directories = client.tenant.directories

        for application in applications:
            print("Application: " application.name)

        for directory in directories:
            print("Directory: " directory.name)

        However, the more readable way is to reference those properties through Client,
        which is a reference to the properties of Tenant:

        applications = client.applications
        directories = client.directories
    """
    NAME = "name"
    KEY = "key"
    APPLICATIONS = "applications"
    DIRECTORIES = "directories"

    @property
    def name(self):
        return self._get_property(self.NAME)

    @property
    def key(self):
        return self._get_property(self.KEY)

    @property
    def applications(self):
        return self._get_resource_property(self.APPLICATIONS, ApplicationList)

    @property
    def directories(self):
        return self._get_resource_property(self.DIRECTORIES, DirectoryList)

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

import json

from stormpath import __version__
from stormpath.http.http_client_request_executor import HttpClientRequestExecutor
from stormpath.http.request_response import Request
from stormpath.util import assert_instance, assert_subclass, assert_true
from stormpath.resource.base import Base
from stormpath.error import Error
from stormpath.resource.error import ResourceError


class DataStore(object):

    DEFAULT_API_VERSION = 1
    DEFAULT_SERVER_HOST = "api.stormpath.com"

    def __init__(self, request_executor, client, base_url=None):

        assert_instance(request_executor, HttpClientRequestExecutor,
            "request_executor")

        self.client = client
        self.base_url = self._get_base_url(base_url)
        self.request_executor = request_executor

    def instantiate(self, cls, properties={}):
        return cls(properties, self.client)

    def get_resource(self, href, cls):

        if self._needs_to_be_fully_qualified(href):
            q_href = self._qualify(href)
        else:
            q_href = href
        properties = self._execute_request('get', q_href, None)
        return self.instantiate(cls, self._to_dict(properties))

    def create(self, parent_href, resource, return_type):

        returned_resource = self._save_resource(parent_href, resource, return_type)

        if isinstance(resource, return_type):
            return resource.set_properties(self._to_dict(returned_resource))

    def save(self, resource, cls=None):

        assert_instance(resource, Base, "resource argument cannot be None")

        href = resource.href

        assert_true(href,
            "save may only be called on objects that have already been persisted"
            + "(i.e. they have an existing href).")
        assert_instance(resource, Base, "resource argument must be instance of Base")

        if self._needs_to_be_fully_qualified(href):
            href = self._qualify(href)

        cls = cls if cls else resource.__class__

        returned_resource = self._save_resource(href, resource, cls)

        # ensure the caller's argument is updated with what is returned:
        resource.set_properties(returned_resource.properties)

        return returned_resource

    def delete(self, resource):

        assert_instance(resource, Base, 'base')

        self._execute_request_('delete', resource.href)

    def _execute_request(self, http_method, href, body=None):
        request = Request(http_method, href, body)
        self._apply_default_request_headers(request)
        response = self.request_executor.execute_request(request)

        result = json.loads(response.body) if response.body else {}

        if response.is_error():
            raise ResourceError(Error(result))

        return result

    def _save_resource(self, href, resource, return_type):

        assert_instance(resource, Base, "resource argument cannot be None.")
        assert_subclass(return_type, Base, "returnType class cannot be null.")

        if self._needs_to_be_fully_qualified(href):
            q_href = self._qualify_(href)
        else:
            q_href = href

        response = self._execute_request('post', q_href, json.dumps(
            self._to_dict(resource)))

        return self.instantiate(return_type, response)

    def _apply_default_request_headers(self, request):
        request.http_headers['Accept'] = 'application/json'
        request.http_headers['User-Agent'] = 'Stormpath-PythonSDK/' + __version__

        if request.body:
            request.http_headers['Content-Type'] = 'application/json'

    def _needs_to_be_fully_qualified(self, href):
        return not href.lower().startswith('http')

    def _qualify(self, href):

        slash_added = '' if href.startswith('/') else '/'

        return self.base_url + slash_added + href

    def _get_base_url(self, base_url):
            if base_url is None:
                return "https://" + self.DEFAULT_SERVER_HOST + "/v" + \
                    str(self.DEFAULT_API_VERSION)
            else:
                return base_url

    def _to_dict(self, resource):

        properties = {}

        for name in resource:

            prop = resource.get(name)

            if isinstance(prop, dict):
                prop = self._to_simple_reference(name, prop)

            properties[name] = prop
        return properties

    def _to_simple_reference(self, property_name, resource_properties):

        href_prop_name = Base.HREF_PROP_NAME
        assert_true(resource_properties and href_prop_name in resource_properties,
         "Nested resource {} must have an 'href' property".format(property_name))

        return {href_prop_name: resource_properties[href_prop_name]}

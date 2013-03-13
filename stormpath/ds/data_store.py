__author__ = 'ecrisostomo'

import json

from stormpath import __version__
from stormpath.http.http_client_request_executor import HttpClientRequestExecutor
from stormpath.http.request_response import Request
from stormpath.util import assert_instance, assert_subclass, assert_true
from stormpath.resource import Resource
from stormpath.resource import Error, ResourceError

DEFAULT_SERVER_HOST = "api.stormpath.com"

class DataStore:

    DEFAULT_API_VERSION = 1

    def __init__(self, request_executor, base_url = DEFAULT_SERVER_HOST):

        assert_instance(request_executor, HttpClientRequestExecutor, "request_executor")

        self.base_url = self._get_base_url_(base_url)
        self.request_executor = request_executor
        self.resource_factory = ResourceFactory(self)

    def instantiate(self, clazz, resource_properties = {}):
        return self.resource_factory.instantiate(clazz, resource_properties)

    def get_resource(self, href, clazz):

        q_href = self._qualify_(href) if self._needs_to_be_fully_qualified_(href) else href
        properties = self._execute_request_('get', q_href)
        return self.resource_factory.instantiate(clazz, properties)

    def create(self, parent_href, resource, return_type):

        returned_resource = self._save_(parent_href, resource, return_type)

        if isinstance(resource, return_type):
            resource.set_properties(returned_resource.properties)

        return returned_resource

    def save(self, resource, clazz = None):

        assert_instance(resource, Resource, "resource")

        href = resource.href
        assert_true(href, "save may only be called on objects that have already been persisted (i.e. they have an existing href).")

        href = self._qualify_(href) if self._needs_to_be_fully_qualified_(href) else href

        clazz = clazz if clazz else resource.__class__

        returned_resource = self._save_(href, resource, clazz)

        # ensure the caller's argument is updated with what is returned from the server:
        resource.set_properties(returned_resource.properties)

        return returned_resource

    def delete(self, resource):

        assert_instance(resource, Resource, 'resource')

        self._execute_request_('delete', resource.href)

    def _execute_request_(self, http_method, href, body = None):
        request = Request(http_method, href, body)
        self._apply_default_request_headers_(request)
        response = self.request_executor.execute_request(request)

        result = json.loads(response.body) if response.body else {}

        if response.is_error():
            raise ResourceError(Error(result))

        return result

    def _save_(self, href, resource, return_type):

        assert_instance(resource, Resource, "resource")
        assert_subclass(return_type, Resource, "return_type")

        q_href = self._qualify_(href) if self._needs_to_be_fully_qualified_(href) else href

        response = self._execute_request_('post', q_href, json.dumps(self._to_dict_(resource)))

        return  self.resource_factory.instantiate(return_type, response)

    def _apply_default_request_headers_(self, request):
        request.http_headers['Accept'] = 'application/json'
        request.http_headers['User-Agent'] = 'Stormpath-PythonSDK/' + __version__

        if request.body:
            request.http_headers['Content-Type'] = 'application/json'

    def _needs_to_be_fully_qualified_(self, href):
        return not href.lower().startswith('http')

    def _qualify_(self, href):

        slash_added =  '' if href.startswith('/') else '/'

        return self.base_url + slash_added + href

    def _get_base_url_(self, base_url):
        return "https://" + DEFAULT_SERVER_HOST + "/v" + str(DataStore.DEFAULT_API_VERSION) \
        if base_url is DEFAULT_SERVER_HOST \
        else base_url

    def _to_dict_(self, resource):

        property_names = resource.property_names
        properties = {}

        for name in property_names:

            prop = resource._get_property_(name)

            if isinstance(prop, dict):
                prop = self._to_simple_reference_(name, prop)

            properties[name] = prop

        return properties


    def _to_simple_reference_(self, property_name, resource_properties):

        href_prop_name = Resource.HREF_PROP_NAME
        assert_true(resource_properties and href_prop_name in resource_properties, "Nested resource {} must have an 'href' property".format(property_name))

        return {href_prop_name : resource_properties[href_prop_name]}


class ResourceFactory:

    def __init__(self, data_store):

        assert_instance(data_store, DataStore, "data_store")
        self.data_store = data_store

    def instantiate(self, resource_clazz, resource_properties = {}):

        assert_subclass(resource_clazz, Resource, "resource_clazz")

        return resource_clazz(self.data_store, resource_properties)



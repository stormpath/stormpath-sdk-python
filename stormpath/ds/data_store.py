__author__ = 'ecrisostomo'

import json

from stormpath import __version__
from stormpath.http.request_response import Request
from stormpath.util import assert_instance, assert_subclass
from stormpath.resource.resource import Resource
from stormpath.resource.resource_error import Error, ResourceError

DEFAULT_SERVER_HOST = "api.stormpath.com"
DEFAULT_API_VERSION = 1

class DataStore:

    def __init__(self, request_executor, base_url = DEFAULT_SERVER_HOST):

        assert_instance(request_executor, ResourceFactory, "request_executor")

        self.base_url = self._get_base_url_(base_url)
        self.request_executor = request_executor
        self.resource_factory = ResourceFactory(self)

    def instantiate(self, clazz, resource_properties = {}):
        return self.resource_factory(clazz, resource_properties)

    def _execute_request_(self, http_method, href, body):
        request = Request(http_method, href, None, {}, body)
        self._apply_default_request_headers_(request)
        response = self.request_executor.execute_request(request)

        result = json.loads(response.body) if len(response.body) else {}

        if response.is_error():
            raise ResourceError(Error(result))

        return result

    def _apply_default_request_headers_(request):
        request.http_headers['Accept'] = 'application/json'
        request.http_headers['User-Agent'] = 'Stormpath-PythonSDK/' + __version__

        if request.body is not None and len(request.body):
            request.http_headers['Content-Type'] = 'application/json'

    def _needs_to_be_fully_qualified_(href):
        return not href.lower().startswith('http')

    def _qualify_(self, href):

        slash_added =  '' if href.startswith('/') else '/'

        return self.base_url + slash_added + href

    def _get_base_url_(base_url):
        return "https://" + DEFAULT_SERVER_HOST + "/v" + str(DEFAULT_API_VERSION) \
        if base_url is DEFAULT_SERVER_HOST \
        else base_url


class ResourceFactory:

    def __init__(self, data_store):

        assert_instance(data_store, DataStore, "data_store")
        self.data_store = data_store

    def instantiate(self, resource_clazz, resource_properties = {}):

        assert_subclass(resource_clazz, Resource, "resource_clazz")

        return resource_clazz(self.data_store, resource_properties)



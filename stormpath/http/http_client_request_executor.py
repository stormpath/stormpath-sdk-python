__author__ = 'ecrisostomo'

import httplib2
import stormpath
from stormpath.http import Request, Response
from stormpath.util import assert_instance

class HttpClientRequestExecutor:

    REDIRECTS_LIMIT = 10

    def __init__(self, api_key = None):
        self.api_key = api_key
        self.http_client = httplib2.Http()
        self.http_client.follow_redirects = False
        self.signer = stormpath.http.Sauthc1Signer()

    def execute_request(self, request, redirects_limit = 10):

        full_request_name = Request.__module__ + "." + Request.__name__
        assert_instance(request, Request, "request argument must be an instance of {}.".format(full_request_name))

        if self.api_key:
            self.signer.sign_request(api_key=self.api_key, request=request)

        self._add_query_string_to_href_(request)

        resp, content = self.http_client.request(request.href, request.http_method, request.body, request.http_headers)

        if self._is_redirect_(resp) and redirects_limit:
            request.href = resp.get('location')
            return self.execute_request(request = request, redirects_limit = redirects_limit - 1)

        return Response(int(resp.status), resp.get('content-type'), content.decode())


    def _add_query_string_to_href_(self, request):

        if (request.href and request.query_string):

            for key, value in request.query_string.items():

                request.href += '&' + '='.join((key, value)) if '?' in request.href else '?' + '='.join((key, value))


    def _is_redirect_(self, response):
        return response.status in [300, 301, 302, 303, 307]
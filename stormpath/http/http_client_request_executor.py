__author__ = 'ecrisostomo'

import httplib2
from stormpath.http.request_response import Request, Response
from stormpath.util import assert_instance

class HttpClientRequestExecutor:

    def __init__(self, api_key):
        self.api_key = api_key
        self.http_client = httplib2.Http()


    def execute_request(self, request):

        full_request_name = Request.__module__ + "." + Request.__name__
        assert_instance(request, Request, "request argument must be an instance of {}.".format(full_request_name))

        self.http_client.add_credentials(self.api_key.id, self.api_key.secret)

        href = request.href

        self._add_query_string_(href, request.query_string)

        resp, content = self.http_client.request(request.href, request.http_method, request.body, request.http_headers)

        return Response(int(resp.status), resp.get('content-type'), content.decode('UTF-8'))


    def _add_query_string_(self, href, query_string):

        if (href and query_string):

            for key, value in query_string:

                href += '&' + '='.join((key, value)) if '?' in href else '?' + '='.join((key, value))


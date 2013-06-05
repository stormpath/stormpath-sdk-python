__author__ = 'ecrisostomo'

from stormpath.util import assert_not_none


class Request(object):

    def __init__(self, http_method, href, body=None, http_headers=None, query_string=None):

        assert_not_none(href, "href cannot be None.")

        split = href.split('?')

        self.query_string = query_string if query_string else {}

        if len(split) > 1:

            self.href = split[0]
            query_string_str = split[1]

            query_string_lst = query_string_str.split('&')

            for pair in query_string_lst:

                pair_lst = pair.split('=')

                self.query_string[pair_lst[0]] = pair_lst[1]

        else:
            self.href = href

        self.http_method = http_method.upper()
        self.http_headers = http_headers if http_headers else {}
        self.body = body

        if self.body is not None:
            self.http_headers['Content-Length'] = str(len(self.body))


class Response(object):

    def __init__(self, http_status, content_type, body):
        self.http_status = http_status
        self.headers = {'content-type': content_type}
        self.body = body

    def is_client_error(self):
        return self.http_status >= 400 and self.http_status < 500

    def is_server_error(self):
        return self.http_status >= 500 and self.http_status < 600

    def is_error(self):
        return self.is_client_error() or self.is_server_error()

__author__ = 'ecrisostomo'

from datetime import datetime
from urllib.parse import urlparse
from uuid import uuid4
from stormpath.util import is_default_port, encode_url, str_query_string

class Sauthc1Signer:

    DEFAULT_ALGORITHM = "SHA256"
    HOST_HEADER = "Host"
    AUTHORIZATION_HEADER = "Authorization"
    STORMPATH_DATE_HEADER = "X-Stormpath-Date"
    ID_TERMINATOR = "sauthc1_request"
    ALGORITHM = "HMAC-SHA-256"
    AUTHENTICATION_SCHEME = "SAuthc1"
    SAUTHC1_ID = "sauthc1Id"
    SAUTHC1_SIGNED_HEADERS = "sauthc1SignedHeaders"
    SAUTHC1_SIGNATURE = "sauthc1Signature"
    DATE_FORMAT = "%Y%m%d"
    TIMESTAMP_FORMAT = "%Y%m%dT%H%M%SZ"
    NL = "\n"

    def sign_request(self, request, api_key):

        time = datetime.utcnow()
        time_stamp = time.strftime(self.TIMESTAMP_FORMAT)
        date_stamp = time.strftime(self.DATE_FORMAT)

        nonce = uuid4()

        parsed_url = urlparse(request.href)

        # SAuthc1 requires that we sign the Host header so we
        # have to have it in the request by the time we sign.
        host_header = parsed_url.hostname

        if not is_default_port(parsed_url):
            host_header = parsed_url.netloc

        request.http_headers[self.HOST_HEADER] = host_header

        request.http_headers[self.STORMPATH_DATE_HEADER] = time_stamp

        method = request.http_method
        canonical_resource_path = self._canonicalize_resource_path_(parsed_url.path)
        canonical_query_string = self._canonicalize_query_string_(request)

    def _canonicalize_query_string_(self, request):
        return str_query_string(request.query_string)

    def _canonicalize_resource_path_(self, resource_path):

        if resource_path:
            return encode_url(resource_path)
        else:
            return '/'



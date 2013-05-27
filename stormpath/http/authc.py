__author__ = 'ecrisostomo'

import binascii
import hmac
import hashlib
from collections import OrderedDict
from datetime import datetime

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

from uuid import uuid4
from stormpath.util import is_default_port, encode_url, str_query_string


class Sauthc1Signer:

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

        nonce = str(uuid4())

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
        canonical_headers_string = self._canonicalize_headers_(request)
        signed_headers_string = self._get_signed_headers_(request)
        request_payload_hash_hex = self._hash_hex_(self._get_request_payload_(request))

        canonical_request = ''.join((method, self.NL,
                                     canonical_resource_path, self.NL,
                                     canonical_query_string, self.NL,
                                     canonical_headers_string, self.NL,
                                     signed_headers_string, self.NL,
                                     request_payload_hash_hex))

        id = ''.join((api_key.id, "/", date_stamp, "/", nonce, "/", self.ID_TERMINATOR))

        canonical_request_hash_hex = self._hash_hex_(canonical_request)

        string_to_sign = ''.join((self.ALGORITHM, self.NL,
                                  time_stamp, self.NL,
                                  id, self.NL,
                                  canonical_request_hash_hex))

        # SAuthc1 uses a series of derived keys, formed by hashing different pieces of data
        k_secret = ''.join((self.AUTHENTICATION_SCHEME, api_key.secret))
        k_date = self._sign_(date_stamp, k_secret)
        k_nonce = self._sign_(nonce, k_date)
        k_signing = self._sign_(self.ID_TERMINATOR, k_nonce)

        signature = self._sign_(string_to_sign, k_signing)
        signature_hex = binascii.hexlify(signature).decode()

        authorization_header = ''.join((self.AUTHENTICATION_SCHEME, " ",
                                        self._create_name_value_pair_(self.SAUTHC1_ID, id), ", ",
                                        self._create_name_value_pair_(self.SAUTHC1_SIGNED_HEADERS, signed_headers_string), ", ",
                                        self._create_name_value_pair_(self.SAUTHC1_SIGNATURE, signature_hex)))

        request.http_headers[self.AUTHORIZATION_HEADER] = authorization_header

    def _create_name_value_pair_(self, name, value):
        return ''.join((name, '=', value))

    def _sign_(self, data, key):

        try:
            byte_key = key.encode()
        except:
            byte_key = key

        return hmac.new(byte_key, data.encode(), hashlib.sha256).digest()

    def _hash_hex_(self, text):
        return hashlib.sha256(text.encode()).hexdigest()

    def _get_request_payload_(self, request):
        return self._get_request_payload_without_query_params_(request)

    def _get_request_payload_without_query_params_(self, request):

        result = ''

        if request.body:
            result = request.body

        return result

    def _get_signed_headers_(self, request):

        sorted_headers = OrderedDict(sorted(request.http_headers.items()))

        result = ''

        for header in sorted_headers.copy().keys():

            if result:
                result += ';' + header
            else:
                result += header

        return result.lower()

    def _canonicalize_headers_(self, request):

        sorted_headers = OrderedDict(sorted(request.http_headers.items()))

        result = ''

        for key, value in sorted_headers.items():

            result += ''.join((str(key).lower(), ':', value))
            result += self.NL

        return result

    def _canonicalize_query_string_(self, request):
        return str_query_string(request.query_string)

    def _canonicalize_resource_path_(self, resource_path):

        if resource_path:
            return encode_url(resource_path)
        else:
            return '/'

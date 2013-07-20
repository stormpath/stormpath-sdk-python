import jprops
import hashlib
import hmac
import binascii
from datetime import datetime
from uuid import uuid4
from requests.auth import HTTPBasicAuth, AuthBase
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse
from stormpath.util import is_default_port, encode_url
from collections import OrderedDict

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


class Sauthc1Signer(AuthBase):

    def __init__(self, id, secret):
        """
        Stormpath custom authentication, based on code from previous SDK to work
        with requests library.

        More info in documentation:
        https://www.stormpath.com/docs/rest/api#DigestAuthenticationHTTPS

        """

        self._id = id
        self._secret = secret
        super(Sauthc1Signer, self).__init__()

    def __call__(self, r):
        # requests library mixes bytes/string in headers,
        # it will be changed in future requests release
        # to native strings.
        # this is a fix to make it work proper with
        # stormpath custom auth.
        headers = {}
        for k, v in r.headers.items():
            if isinstance(k, bytes):
                k = k.decode('utf-8')
            headers[k] = v
        r.headers.clear()
        r.headers.update(headers)

        time = datetime.utcnow()
        time_stamp = time.strftime(TIMESTAMP_FORMAT)
        date_stamp = time.strftime(DATE_FORMAT)

        nonce = str(uuid4())

        parsed_url = urlparse(r.url)

        # SAuthc1 requires that we sign the Host header so we
        # have to have it in the request by the time we sign.
        host_header = parsed_url.hostname

        if not is_default_port(parsed_url):
            host_header = parsed_url.netloc

        r.headers[HOST_HEADER] = host_header
        r.headers[STORMPATH_DATE_HEADER] = time_stamp

        method = r.method
        if parsed_url.path:
            canonical_resource_path = encode_url(parsed_url.path)
        else:
            canonical_resource_path = '/'

        canonical_query_string = ''
        if parsed_url.query:
            canonical_query_string = parsed_url.query

        sorted_headers = OrderedDict(sorted(r.headers.items()))
        canonical_headers_string = ''
        for key, value in sorted_headers.items():
            canonical_headers_string += "%s:%s%s" % (key.lower(), value, NL)

        signed_headers_string = ';'.join(sorted_headers.keys()).lower()

        request_payload_hash_hex = hashlib.sha256(
            (r.body or '').encode()).hexdigest()

        canonical_request = "%s%s%s%s%s%s%s%s%s%s%s" % (
            method, NL, canonical_resource_path, NL, canonical_query_string,
            NL, canonical_headers_string, NL, signed_headers_string,
            NL, request_payload_hash_hex)

        id = "%s/%s/%s/%s" % (self._id, date_stamp, nonce, ID_TERMINATOR)

        canonical_request_hash_hex = hashlib.sha256(
            canonical_request.encode()).hexdigest()

        string_to_sign = "%s%s%s%s%s%s%s" % (
            ALGORITHM, NL, time_stamp, NL, id, NL, canonical_request_hash_hex)

        def _sign(data, key):
            try:
                byte_key = key.encode()
            except:
                byte_key = key

            return hmac.new(byte_key, data.encode(), hashlib.sha256).digest()

        # SAuthc1 uses a series of derived keys, formed by hashing different
        # pieces of data
        k_secret = "%s%s" % (AUTHENTICATION_SCHEME, self._secret)
        k_date = _sign(date_stamp, k_secret)
        k_nonce = _sign(nonce, k_date)
        k_signing = _sign(ID_TERMINATOR, k_nonce)

        signature = _sign(string_to_sign, k_signing)
        signature_hex = binascii.hexlify(signature).decode()

        authorization_header = ', '.join((
            "%s %s=%s" % (AUTHENTICATION_SCHEME, SAUTHC1_ID, id),
            "%s=%s" % (SAUTHC1_SIGNED_HEADERS, signed_headers_string),
            "%s=%s" % (SAUTHC1_SIGNATURE, signature_hex),
        ))

        r.headers[AUTHORIZATION_HEADER] = authorization_header

        return r


class Auth(object):

    """
    Auth class is used to provide a proper authentication for requests library
    based on any valid authentication source with Stormpath API key.

    """

    def __init__(self, api_key_file_location=None,
                 api_key_id_property_name='apiKey.id',
                 api_key_secret_property_name='apiKey.secret',
                 api_key=None, id=None, secret=None, api_url=None,
                 **kwargs):
        """
        Checks various authentication sources for an API key and
        uses first available.

        """

        self._id = None
        self._secret = None

        # if `api_key_file_location` is available extract key/secret
        # and ignore other authentication sources.
        # key/secret are extracted based on property names
        if api_key_file_location:
            with open(api_key_file_location, 'rb') as fp:
                cred = jprops.load_properties(fp)
                self._id = cred.get(api_key_id_property_name)
                self._secret = cred.get(api_key_secret_property_name)
                del cred
            return

        # if `api_key` is available extract key/secret
        # and ignore other authentication sources
        if api_key:
            self._id, self._secret = api_key.get('id'), api_key.get('secret')
            return

        # if `id` and `secret` are available use them
        # and ignore other authentication sources
        if id and secret:
            self._id, self._secret = id, secret
            return

        raise Exception('Valid authentication source not found.')

    def __call__(self):
        return self.basic

    @property
    def id(self):
        return self._id

    @property
    def secret(self):
        return self._secret

    @property
    def basic(self):
        """
        Returns basic http authentication handler which can be used with requests library.

        https://www.stormpath.com/docs/rest/api#BaseAuthenticationHTTPS

        """
        return HTTPBasicAuth(self._id, self._secret)

    @property
    def digest(self):
        """
        Returns custom authentication handler which can be used with requests library.
        It uses Stormpath custom digests authentication.

        https://www.stormpath.com/docs/rest/api#DigestAuthenticationHTTPS

        """

        return Sauthc1Signer(self._id, self._secret)

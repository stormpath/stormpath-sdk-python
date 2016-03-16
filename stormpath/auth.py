"""Authentication library and utilities."""


import hashlib
import hmac
import binascii
from datetime import datetime
from uuid import uuid4
from requests.auth import HTTPBasicAuth, AuthBase
from collections import OrderedDict
from os import environ
from os.path import exists, expanduser, isfile, join

from requests.utils import to_native_string

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse


HOST_HEADER = 'Host'
AUTHORIZATION_HEADER = 'Authorization'
STORMPATH_DATE_HEADER = 'X-Stormpath-Date'
ID_TERMINATOR = 'sauthc1_request'
ALGORITHM = 'HMAC-SHA-256'
AUTHENTICATION_SCHEME = 'SAuthc1'
SAUTHC1_ID = 'sauthc1Id'
SAUTHC1_SIGNED_HEADERS = 'sauthc1SignedHeaders'
SAUTHC1_SIGNATURE = 'sauthc1Signature'
DATE_FORMAT = '%Y%m%d'
TIMESTAMP_FORMAT = '%Y%m%dT%H%M%SZ'
NL = '\n'


class Sauthc1Signer(AuthBase):
    """StormPath auth request signer for custom digest auth.

    The implementation hooks into the Python Requests library to automatically
    sign all the requests using this auth mechanism.

    More info in documentation:
    https://www.stormpath.com/docs/rest/api#DigestAuthenticationHTTPS
    """

    def __init__(self, id, secret):
        """Initialize new digest auth mechanism with provided id and secret."""
        super(Sauthc1Signer, self).__init__()
        self._id = id
        self._secret = secret

    @staticmethod
    def _is_default_port(parsed_url):
        scheme = parsed_url.scheme.lower()
        port = parsed_url.port

        return not port or (port == 80 and scheme == 'http') or \
            (port == 443 and scheme == 'https')

    @staticmethod
    def _encode_url(query):
        str_dict = {'+': '%20', '*': '%2A', '%7E': '~'}
        for key, value in str_dict.items():
            if key in query:
                query = query.replace(key, value)

        return query

    @staticmethod
    def _order_query_params(query):
        ordered_query_params = sorted(query.split('&'))

        return '&'.join(ordered_query_params)

    def __call__(self, r):
        time = datetime.utcnow()
        time_stamp = time.strftime(TIMESTAMP_FORMAT)
        date_stamp = time.strftime(DATE_FORMAT)

        nonce = str(uuid4())
        parsed_url = urlparse(r.url)

        # SAuthc1 requires that we sign the Host header so we
        # have to have it in the request by the time we sign.
        host_header = parsed_url.hostname

        if not self._is_default_port(parsed_url):
            host_header = parsed_url.netloc

        r.headers[HOST_HEADER] = host_header
        r.headers[STORMPATH_DATE_HEADER] = time_stamp

        method = r.method
        if parsed_url.path:
            canonical_resource_path = self._encode_url(parsed_url.path)
        else:
            canonical_resource_path = '/'

        canonical_query_string = ''
        if parsed_url.query:
            canonical_query_string = self._encode_url(
                    self._order_query_params(parsed_url.query))

        auth_headers = r.headers.copy()

        # FIXME: REST API doesn't want this header in the signature.
        if 'Content-Length' in auth_headers:
            del auth_headers['Content-Length']
        # Connection header can be transparently overridden by proxies anywhere and should not
        # be a part of sig computation
        if 'Connection' in auth_headers:
            del auth_headers['Connection']

        sorted_headers = OrderedDict(sorted(auth_headers.items()))
        canonical_headers_string = ''
        for key, value in sorted_headers.items():
            canonical_headers_string += '%s:%s%s' % (key.lower(), value, NL)

        signed_headers_string = ';'.join(sorted_headers.keys()).lower()

        request_payload_hash_hex = hashlib.sha256(
            (r.body or '').encode()).hexdigest()

        canonical_request = '%s%s%s%s%s%s%s%s%s%s%s' % (
            method, NL, canonical_resource_path, NL, canonical_query_string,
            NL, canonical_headers_string, NL, signed_headers_string,
            NL, request_payload_hash_hex)

        id = '%s/%s/%s/%s' % (self._id, date_stamp, nonce, ID_TERMINATOR)

        canonical_request_hash_hex = hashlib.sha256(
            canonical_request.encode()).hexdigest()

        string_to_sign = '%s%s%s%s%s%s%s' % (
            ALGORITHM, NL, time_stamp, NL, id, NL, canonical_request_hash_hex)

        def _sign(data, key):
            try:
                byte_key = key.encode()
            except Exception:
                byte_key = key

            return hmac.new(byte_key, data.encode(), hashlib.sha256).digest()

        # SAuthc1 uses a series of derived keys, formed by hashing different
        # pieces of data.
        k_secret = '%s%s' % (AUTHENTICATION_SCHEME, self._secret)
        k_date = _sign(date_stamp, k_secret)
        k_nonce = _sign(nonce, k_date)
        k_signing = _sign(ID_TERMINATOR, k_nonce)

        signature = _sign(string_to_sign, k_signing)
        signature_hex = binascii.hexlify(signature).decode()

        authorization_header = ', '.join((
            '%s %s=%s' % (AUTHENTICATION_SCHEME, SAUTHC1_ID, id),
            '%s=%s' % (SAUTHC1_SIGNED_HEADERS, signed_headers_string),
            '%s=%s' % (SAUTHC1_SIGNATURE, signature_hex),
        ))

        r.headers[AUTHORIZATION_HEADER] = to_native_string(authorization_header)

        return r


class Auth(object):
    """Provides authentication for StormPath API requests."""

    def __init__(self, api_key_file_location=None,
            api_key_file=None,
            api_key_id_property_name='apiKey.id',
            api_key_secret_property_name='apiKey.secret',
            api_key=None, id=None, secret=None, scheme='SAuthc1',
            api_key_id=None, api_key_secret=None,
            method=None):
        """
        Initialize authentication using one of the available authentication
        credentials source:

        :param api_key_file: Location of the API key file (in the Java
        .properties file format) (default: API key file not used)
        :param api_key_id_property_name: Name of the `ID` property in the
            key file (default: apiKey.id)
        :param api_key_secret_property_name: Name of the `secret` property
            in the key file (default: apiKey.secret)
        :param api_key: A dictionary-like object containing the `id` and
            `secret` keys mapped to the API ID and secret respectively
        :param api_key_id: ID (if directly provided; default is None)
        :param api_key_secret: secret (if directly provided; default is None)
        :param scheme: authentication scheme (`Sauthc1` or `basic`, default is
            `Sauthc1`)

        All available authentication credentials sources are checked, in this
        priority:

        1. API key file (if `api_key_file` is set and the file exists)
        2. API key dict (if `api_key` contains `id` and `secret` keys)
        3. API key `api_key_id` and `api_key_secret` parameters
        4. STORMPATH_API_KEY_FILE as an environment variable.
        4. STORMPATH_API_KEY_ID and STORMPATH_API_KEY_SECRET as environment
           variables.

        The `api_key_id` and `api_key_secret` can be accessed as attributes.

        The default authentication scheme is `Sauthc1`, and is strongly
        recommended. In cases where it can't be used (for example, in Google
        App Engine), basic authentication can be selected instead by supplying
        `basic` as the authentication scheme.

        Once initialized, `scheme` property will return the authentication
        scheme implementation selected.
        """
        self._api_key_id = None
        self._api_key_secret = None
        self._scheme = scheme

        # backwards compatibility, in case anyone used it
        if method is not None:
            self._scheme = 'basic' if method == 'basic' else 'SAuthc1'

        if self._read_api_key_file(api_key_file or api_key_file_location,
                api_key_id_property_name, api_key_secret_property_name):
            return

        if api_key and 'id' in api_key and 'secret' in api_key:
            self._api_key_id = api_key['id']
            self._api_key_secret = api_key['secret']

            return

        if api_key and 'api_key_id' in api_key and 'api_key_secret' in api_key:
            self._api_key_id = api_key['api_key_id']
            self._api_key_secret = api_key['api_key_secret']

            return

        if id and secret:
            self._api_key_id = id
            self._api_key_secret = secret

            return

        if api_key_id and api_key_secret:
            self._api_key_id = api_key_id
            self._api_key_secret = api_key_secret

            return

        if self._read_api_key_file(environ.get('STORMPATH_API_KEY_FILE'),
                api_key_id_property_name, api_key_secret_property_name):
            return

        if environ.get('STORMPATH_API_KEY_ID') and environ.get('STORMPATH_API_KEY_SECRET'):
            self._api_key_id = environ.get('STORMPATH_API_KEY_ID')
            self._api_key_secret = environ.get('STORMPATH_API_KEY_SECRET')

            return

        default_file = join(expanduser('~'), '.stormpath', 'apiKey.properties')
        if exists(default_file) and self._read_api_key_file(default_file,
                api_key_id_property_name, api_key_secret_property_name):
            return

        raise ValueError('No valid authentication sources found')

    @staticmethod
    def _load_properties(fname):
        import codecs

        props = {}
        if not fname or not isfile(fname):
            return props

        try:
            with codecs.open(fname, 'r', encoding='utf-8') as fd:
                for line in fd:
                    line = line.strip()
                    if line.startswith('#') or '=' not in line:
                        continue

                    k, v = line.split('=', 1)
                    props[k.strip()] = v.strip()

            return props
        except UnicodeDecodeError:
            return {}

    def _read_api_key_file(self, fname, id_name, secret_name):
        cred = self._load_properties(fname)
        self._api_key_id = cred.get(id_name)
        self._api_key_secret = cred.get(secret_name)

        return (self._api_key_id and self._api_key_secret)

    def __call__(self):
        return self.signer

    @property
    def id(self):
        return self._api_key_id

    @property
    def secret(self):
        return self._api_key_secret

    @property
    def basic(self):
        """
        Returns basic http authentication handler which can be used with
        Python Requests library.

        http://docs.stormpath.com/rest/product-guide/#authentication
        """
        return HTTPBasicAuth(self._api_key_id, self._api_key_secret)

    @property
    def digest(self):
        """
        Returns custom authentication handler which can be used with
        Python requests library, and which uses Stormpath custom digest
        authentication.

        http://docs.stormpath.com/rest/product-guide/#authentication
        """
        return Sauthc1Signer(self._api_key_id, self._api_key_secret)

    @property
    def signer(self):
        """Deprecated, use Auth.scheme instead."""
        return self.scheme

    @property
    def scheme(self):
        """Selected authentication scheme implementation."""
        if self._scheme == 'basic':
            return self.basic
        elif self._scheme == 'SAuthc1':
            return self.digest
        else:
            raise ValueError('Unsupported auth scheme ' + str(self._scheme))

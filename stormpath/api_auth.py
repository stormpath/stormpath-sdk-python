import base64
import datetime
import json
try:
    from urlparse import urlparse, parse_qs
except ImportError:
    from urllib.parse import urlparse, parse_qs

import jwt
from oauthlib.oauth2 import RequestValidator as Oauth2RequestValidator
from oauthlib.oauth2 import BackendApplicationServer as Oauth2BackendApplicationServer
from oauthlib.oauth2 import BackendApplicationClient as Oauth2BackendApplicationClient
from oauthlib.common import to_unicode

from stormpath.error import Error as StormpathError


GRANT_TYPE_CLIENT_CREDENTIALS = 'client_credentials'
GRANT_TYPES = [GRANT_TYPE_CLIENT_CREDENTIALS]
DEFAULT_TTL = 3600
DEFAULT_ACCESS_TOKEN_LOCATIONS = ['header', 'body']
VALID_ACCESS_TOKEN_LOCATIONS = ['header', 'body', 'url']


class DummyRequest(object):
    """Used to model the same flow for Basic and Bearer"""
    def __init__(self, api_key):
        self.account = None
        self.api_key = api_key


class SPBasicAuthRequestValidator(object):
    def __init__(self, app, headers):
        self.authorization = headers.get('Authorization')
        self.app = app
        self.client_id = None
        self.client_secret = None

    def extract_client_data(self):
        _, b64encoded_data = self.authorization.split(' ')
        decoded_data = to_unicode(
            base64.b64decode(b64encoded_data.encode('utf-8')), 'ascii')
        self.client_id, self.client_secret = decoded_data.split(':')

    def verify_request(self):
        self.extract_client_data()
        if self.client_id and self.client_secret:
            key = self.app.api_keys.get_key(self.client_id, self.client_secret)
            return (key and key.is_enabled()), DummyRequest(api_key=key)
        return None, None


class AccessToken(object):
    def __init__(self, app, token):
        self.token = token
        self.app = app
        self.token_scopes = []
        self.account = None
        self.api_key = None
        self.for_api_key = True

        # get raw data without validation
        try:
            data = jwt.decode(self.token, verify=False, algorithms=['HS256'])
            self.client_id = data.get('sub', '')
            try:
                self.account = self.app.accounts.get(data.get('sub', ''))

                # We're accessing account.username here to force
                # evaluation of this Account -- this allows us to check
                # and see whether or not this Account is actually
                # valid.
                self.account.username
            except StormpathError:
                self.account = None
            if self.account:
                self.for_api_key = False
            self.api_key = self.app.api_keys.get_key(self.client_id)
            self.exp = data.get('exp', 0)
            self.scopes = data.get('scope', '') if data.get('scope') else ''
            self.scopes = self.scopes.split(' ')
        except jwt.DecodeError:
            pass

    def __repr__(self):
        return self.token

    def _is_valid(self):
        if self.for_api_key:
            valid = self.api_key and self.api_key.is_enabled()
        else:
            valid = bool(self.account)

        if valid and \
                datetime.datetime.utcnow() < \
                    datetime.datetime.utcfromtimestamp(float(self.exp)):

            try:
                jwt.decode(
                    self.token, self.app._client.auth.secret,
                    algorithms=['HS256'])
            except jwt.DecodeError:
                return False

            return True
        return False

    def _within_scope(self, scopes):
        return set(scopes).issubset(set(self.scopes))

    def to_json(self):
        return json.dumps({'access_token': self.token,
                'expires_in': self.exp,
                'scope': ' '.join(self.scopes),
                'token_type': 'jwt-bearer'})


class ApiAuthenticationResult(object):
    def __init__(self, account, api_key, access_token):
        self.api_key = api_key
        self.token = access_token
        self.account = self.api_key.account if self.api_key else account


class SPOauth2RequestValidator(Oauth2RequestValidator):
    def __init__(self, app=None, allowed_scopes=[], ttl=DEFAULT_TTL):
        super(SPOauth2RequestValidator, self).__init__()
        self.allowed_scopes = allowed_scopes
        self.app = app
        self.ttl = ttl

    def validate_client_id(self, client_id, request, *args, **kwargs):
        key = self.app.api_keys.get_key(client_id)
        return key and key.is_enabled()

    def validate_scopes(self, client_id, scopes, client, request, *args, **kwargs):
        all_scopes = set(self.allowed_scopes)
        requested_scopes = set(scopes)
        return requested_scopes.issubset(all_scopes)

    def get_default_scopes(self, client_id, request, *args, **kwargs):
        # Scopes a client will authorize for if none are supplied in the
        # authorization request.
        return []

    def authenticate_client(self, request, *args, **kwargs):
        request.app = self.app
        request.expires_in = self.ttl
        authorization = request.headers.get('Authorization')
        try:
            auth_scheme, b64encoded_data = authorization.split(' ')
            decoded_data = to_unicode(
                base64.b64decode(b64encoded_data.encode('utf-8')), 'ascii')
            client_id, _ = decoded_data.split(':')
            request.client = Oauth2BackendApplicationClient(client_id)
        except Exception:
            return False
        if self.validate_client_id(client_id, request):
            return True
        return False

    def authenticate_client_id(self, client_id, request, *args, **kwargs):
        return False

    def validate_grant_type(self, client_id, grant_type, client, request, *args, **kwargs):
        return grant_type == GRANT_TYPE_CLIENT_CREDENTIALS

    def save_bearer_token(self, token, request, *args, **kwargs):
        # The access token is stateless so we don't need to save it
        pass

    def validate_bearer_token(self, token, scopes, request):
        # Remember to check expiration and scope membership
        access_token = AccessToken(self.app, token)
        request.account = access_token.account
        request.api_key = access_token.api_key
        if access_token._is_valid() and access_token._within_scope(scopes):
            return True
        return False


def _generate_signed_token(request):
    client_id = request.client.client_id
    request.app.api_keys.get_key(client_id)

    # the SP ApiKey is already validated in SPOauth2RequestValidator.validate_client_id
    # but to prevent time based attacks oauthlib always goes through the entire
    # flow  even though the entire request will be deemed invalid
    # in the end.
    secret = request.app._client.auth.secret

    now = datetime.datetime.utcnow()

    data = {
        'iss': request.app.href,
        'sub': client_id,
        'iat': now,
        'exp': now + datetime.timedelta(seconds=request.expires_in)
    }

    if hasattr(request, 'scope'):
        data['scope'] = request.scope

    token = jwt.encode(data, secret, 'HS256')
    token = to_unicode(token, "UTF-8")

    return token


def _get_bearer_token(app, allowed_scopes, http_method, uri, body, headers, ttl=DEFAULT_TTL):
    validator = SPOauth2RequestValidator(app=app, allowed_scopes=allowed_scopes, ttl=ttl)
    server = Oauth2BackendApplicationServer(validator,
        token_generator=_generate_signed_token)

    headers, body, status = server.create_token_response(
        uri, http_method, body, headers, {})

    if status == 200:
        token_response = json.loads(body)
        return token_response.get('access_token')
    return None


def _authenticate_request(auth_type, app, allowed_scopes, http_method,
                          uri, body, headers, ttl=DEFAULT_TTL):
    if auth_type == 'Basic':
        validator = SPBasicAuthRequestValidator(app=app, headers=headers)
        valid, r = validator.verify_request()
        return valid, r
    if auth_type == 'Bearer':
        validator = SPOauth2RequestValidator(app=app, allowed_scopes=allowed_scopes, ttl=ttl)
        server = Oauth2BackendApplicationServer(validator)
        valid, r = server.verify_request(uri, http_method, body, headers, allowed_scopes)
        return valid, r
    return None, None


def authenticate(app=None, allowed_scopes=None, http_method='', uri='',
                 body=None, headers=None, ttl=DEFAULT_TTL, locations=None):
    if body is None:
        body = {}
    if headers is None:
        raise ValueError("headers can't be None")
    if allowed_scopes is None:
        allowed_scopes = []
    if locations is None:
        locations = DEFAULT_ACCESS_TOKEN_LOCATIONS
    else:
        locations = list(set(locations) & set(VALID_ACCESS_TOKEN_LOCATIONS))
    for k, v in headers.items():
        headers[k] = to_unicode(v, 'ascii')
    jwt_token = None
    access_token = None
    auth_scheme = None
    url_qs = parse_qs(urlparse(uri).query)

    if 'url' in locations and 'access_token' in url_qs:
        auth_scheme = 'Bearer'
        jwt_token = url_qs.get('access_token')[0]
    elif 'header' in locations and 'Authorization' in headers:
        auth_header = headers.get('Authorization')
        auth_scheme = auth_header.split(' ')[0]
        if auth_scheme == 'Basic':
            if body.get('grant_type') or url_qs.get('grant_type'):
                jwt_token = _get_bearer_token(
                    app, allowed_scopes, http_method, uri, body, headers,
                    ttl=ttl)
        if auth_scheme == 'Bearer':
            jwt_token = auth_header.split(' ')[1]
    elif 'body' in locations and 'access_token' in body:
        auth_scheme = 'Bearer'
        jwt_token = body.get('access_token')

    if jwt_token:
        access_token = AccessToken(app, jwt_token)

    valid, r = _authenticate_request(
        auth_scheme, app, allowed_scopes, http_method, uri, body, headers,
        ttl=ttl)
    if not valid:
        return None
    return ApiAuthenticationResult(
        account=r.account, api_key=r.api_key, access_token=access_token)

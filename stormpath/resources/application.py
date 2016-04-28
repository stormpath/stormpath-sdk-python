"""Stormpath Application resource mappings."""

from datetime import datetime
from uuid import uuid4
try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode
try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse
try:
    from urlparse import parse_qs
except ImportError:
    from urllib.parse import parse_qs

import jwt
from oauthlib.common import to_unicode

from .base import (
    CollectionResource,
    DeleteMixin,
    DictMixin,
    ListOnResource,
    Resource,
    SaveMixin,
    StatusMixin,
    AutoSaveMixin,
)
from .login_attempt import LoginAttemptList
from .password_reset_token import PasswordResetTokenList
from .organization import Organization
from .saml_policy import SamlPolicy
from ..api_auth import LEEWAY
from ..error import Error as StormpathError
from ..nonce import Nonce


class StormpathCallbackResult(object):
    def __init__(self, account, state, status):
        self.account = account
        self.state = state
        self.status = status


class Application(Resource, DeleteMixin, DictMixin, AutoSaveMixin, SaveMixin, StatusMixin):
    """Stormpath Application resource.

    More info in documentation:
    http://docs.stormpath.com/python/product-guide/#applications
    """

    SSO_ENDPOINT = "https://api.stormpath.com/sso"
    SSO_LOGOUT_ENDPOINT = SSO_ENDPOINT + "/logout"

    autosaves = ('custom_data',)
    writable_attrs = (
        'authorized_callback_uris',
        'custom_data',
        'description',
        'name',
        'saml_policy',
        'status',
    )
    resolvable_attrs = (
        'name',
    )

    @staticmethod
    def get_resource_attributes():
        from .account import AccountList
        from .account_store_mapping import (
            AccountStoreMapping,
            AccountStoreMappingList,
        )
        from .api_key import ApiKeyList
        from .auth_token import AuthTokenList
        from .group import GroupList
        from .tenant import Tenant
        from .custom_data import CustomData
        from .verification_email import VerificationEmailList
        from .oauth_policy import OauthPolicy

        return {
            'authorized_callback_uris': ListOnResource,
            'custom_data': CustomData,
            'accounts': AccountList,
            'account_store_mappings': AccountStoreMappingList,
            'api_keys': ApiKeyList,
            'auth_tokens': AuthTokenList,
            'default_account_store_mapping': AccountStoreMapping,
            'default_group_store_mapping': AccountStoreMapping,
            'groups': GroupList,
            'login_attempts': LoginAttemptList,
            'oauth_policy': OauthPolicy,
            'password_reset_tokens': PasswordResetTokenList,
            'saml_policy': SamlPolicy,
            'tenant': Tenant,
            'verification_emails': VerificationEmailList
        }

    def authenticate_account(self, login, password, expand=None,
            account_store=None, organization_name_key=None):
        """Authenticate Account inside the Application.

        :param login: Username or email address

        :param password: Unencrypted user password

        :param expand:
            A :class:`stormpath.resources.base.Expansion` object (optional)

        :param account_store:
            A specific :class:`stormpath.resources.account_store.AccountStore`
            object to authenticate against (optional)
        """
        return self.login_attempts.basic_auth(
            login, password, expand, account_store,
            organization_name_key=organization_name_key, app=self)

    def get_provider_account(self, provider, **provider_kwargs):
        """Used for getting account data from 3rd party Providers
        (ie. Google, Facebook)

        :param provider: Can be one of the following Constants:

            * :const:`stormpath.resources.provider.Provider.GOOGLE`
            * :const:`stormpath.resources.provider.Provider.FACEBOOK`
            * :const:`stormpath.resources.provider.Provider.STORMPATH`


        :param provider_kwargs: Which specific kwargs are needed depends on the chosen Provider.

            {
                'code': '...',
                'access_token': '...',
                'client_id': '...',
                'client_secret': '...'
            }
        """
        provider_data = provider_kwargs.copy()
        provider_data['provider_id'] = provider

        return self.accounts.create({
            'provider_data': provider_data
        })

    def send_password_reset_email(self, email, account_store=None):
        """Send a password reset email.

        More info in documentation:
        http://docs.stormpath.com/rest/product-guide/#reset-an-accounts-password

        :param email: Email address to send the email to.
        :param account_store: Account store that holds the account with the given email.
            This parameter is optional. If no account store is given Stormpath will
            use the default account store for this application.
        """
        params = {'email': email}
        if account_store:
            href = account_store.href if isinstance(account_store, Resource) else account_store
            params.update({'account_store': {'href': href}})
        token = self.password_reset_tokens.create(params)
        return token.account

    def verify_password_reset_token(self, token):
        """Verify password reset by using a token.

        :param token: a string representation of the password reset token extracted from the URL.
        """
        return self.password_reset_tokens[token].account

    def reset_account_password(self, token, password):
        """Resets the password for an account.

        :param token: a string representation of the password reset token extracted from the URL.
        :param password: new password
        """
        token = self.password_reset_tokens[token]
        if token.account.email not in [a.email for a in self.accounts]:
            raise ValueError('Unrecognized account for this application %s' %
                repr(token.account))

        href = self.password_reset_tokens.build_reset_href(token)
        data = {'password': password}
        self._store.create_resource(href=href, data=data)

    def build_id_site_redirect_url(self, callback_uri, path=None, state=None, logout=False,
                                   show_organization_field=False, sp_token=None,
                                   organization_name_key=None):
        """Builds a redirect uri for ID site.

        :param callback_uri: Callback URI to witch Stormpaath will redirect after
            the user has entered their credentials on the ID site. Note: For security reasons
            this is required to be the same as "Authorized Redirect URI" in the
            Admin Console's ID Site settings.

        :param path:
            An optional string indicating to wich template we should redirect the user to.
            By default it will redirect to the login screen but you can redirect to the
            registration or forgot password screen with '/#/register' and '/#/forgot' respectively.

        :param state: an optional string that stores information that your application needs
            after the user is redirected back to your application

        :param logout: a Boolean value indicating if this should redirect to the logout endpoint

        :param show_organization_field bool: If True, will display organization name field
            to user on ID Site login page.  Default False.

        :param sp_token string: JWT used for password rest.  See
            https://docs.stormpath.com/rest/product-guide/latest/idsite.html?highlight=sp_token#resetting-your-password-with-id-site

        :param organization_name_key string: If set, the users credentials will be tried
            against only this organization.  Default is not set.

        :return: A URI to witch to redirect the user.
        """
        api_key_secret = self._client.auth.secret
        api_key_id = self._client.auth.id

        endpoint = self.SSO_LOGOUT_ENDPOINT if logout else self.SSO_ENDPOINT

        body = {
            'iat': datetime.utcnow(),
            'jti': uuid4().hex,
            'iss': api_key_id,
            'sub': self.href,
            'cb_uri': callback_uri,
            'sof': show_organization_field,
        }

        if sp_token is not None:
            body['sp_token'] = sp_token

        if organization_name_key is not None:
            body['onk'] = organization_name_key

        if path:
            body['path'] = path
        if state:
            body['state'] = state

        jwt_signature = to_unicode(jwt.encode(body, api_key_secret, 'HS256'), 'UTF-8')
        url_params = {'jwtRequest': jwt_signature}
        return endpoint + '?' + urlencode(url_params)

    def has_account(self, account):
        for app in account.applications:
            if app.href == self.href:
                return True
        return False

    def build_saml_idp_redirect_url(self, callback_uri, saml_provider_endpoint,
                                    path=None, state=None, account_store=None,
                                    organization=None, logout=False):
        """Builds a redirect uri for SAML IdP.

        :param callback_uri: Callback URI to which Stormpath will redirect after
            the user has entered their credentials on the ID site. Note: For security reasons
            this is required to be the same as "Authorized Callback URIs" in the
            Admin Console's Application settings.

        :param saml_provider_endpoint:
            SAML SSO Initiation Endpoint from SAML Policy resource on Application.

        :param path:
            An optional string indicating to wich template we should redirect the user to.
            By default it will redirect to the login screen but you can redirect to the
            registration or forgot password screen with '/#/register' and '/#/forgot' respectively.

        :param state: an optional string that stores information that your application needs
            after the user is redirected back to your application

        :param account_store: an optional parameter that specifies an
            Account Store to attempt to authenticate against.

        :param organization: an optional parameter that specifies an
            Organization that is an Account Store for your application.
            This is used for multitenant applications that use SAML.

        :param logout: a Boolean value indicating if this should redirect to the logout endpoint

        :return: A URI to which to redirect the user.
        """
        api_key_secret = self._client.auth.secret
        api_key_id = self._client.auth.id

        endpoint = saml_provider_endpoint
        if logout:
            raise NotImplementedError('Logout feature is not implemented yet.')

        try:
            jti = uuid4().get_hex()
        except AttributeError:
            jti = uuid4().hex

        body = {
            'iat': datetime.utcnow(),
            'jti': jti,
            'iss': api_key_id,
            'sub': self.href,
            'cb_uri': callback_uri,
        }
        if path:
            body['path'] = path
        if state:
            body['state'] = state
        if account_store:
            if hasattr(account_store, 'href'):
                account_store = account_store.href
            body['ash'] = account_store
        if organization:
            if isinstance(organization, Organization):
                organization = organization.name_key
            body['onk'] = organization

        jwt_signature = to_unicode(
            jwt.encode(
                body, api_key_secret, 'HS256', headers={'kid': api_key_id}),
            'UTF-8')
        url_params = {'accessToken': jwt_signature}
        return endpoint + '?' + urlencode(url_params)

    def handle_stormpath_callback(self, url_response):
        """Handles the callback to Stormpath (for example, from the ID
        site or SAML Iderntity Provider).

        :param url_response: A string representing the full url (with
            it's params) to which the ID redirected to.

        :return: A :class:`stormpath.resources.application.StormpathCallbackResult`
            object. Which holds the
            :class:`stormpath.resources.account.Account` object, status
            and the state (if any was passed along when creating the
            redirect uri).
        """
        url_info = urlparse(url_response)
        query_params = parse_qs(url_info.query)
        jwt_response_params = query_params.get("jwtResponse")
        if not jwt_response_params or len(jwt_response_params) != 1:
            return None
        jwt_response = jwt_response_params[0]
        api_key_secret = self._client.auth.secret

        # validate signature
        try:
            decoded_data = jwt.decode(
                jwt_response, api_key_secret, audience=self._client.auth.id,
                algorithms=['HS256'], leeway=LEEWAY)
        except (jwt.DecodeError, jwt.ExpiredSignature):
            return None
        except jwt.MissingRequiredClaimError as missing_claim_error:
            if missing_claim_error.claim != 'aud':
                return None

            decoded_data = jwt.decode(
                jwt_response, api_key_secret, algorithms=['HS256'],
                leeway=LEEWAY)

            if 'err' in decoded_data:
                raise StormpathError(decoded_data.get('err'))
            else:
                raise missing_claim_error

        nonce = Nonce(decoded_data['irt'])

        # check if nonce is in cache already
        # if it is throw an Exception
        if self._store._cache_get(nonce.href):
            raise ValueError('JWT has already been used.')

        # store nonce in cache store
        self._store._cache_put(href=nonce.href, data={'value': nonce.value})

        # issuer = decoded_data['iss']
        account_href = decoded_data['sub']
        is_new_account = decoded_data['isNewSub']
        state = decoded_data.get('state')
        status = decoded_data.get('status')

        if account_href:
            account = self.accounts.get(account_href)
            if self.has_account(account):
                # We modify the internal parameter sp_http_status which indicates if an account
                # is new (ie. just created). This is so we can take advantage of the account.is_new_account
                # property
                account.sp_http_status  # NOTE: this forces account retrieval and building of the actual Account object
                account.__dict__['sp_http_status'] = 201 if is_new_account else 200
            else:
                account = None
        else:
            account = None

        return StormpathCallbackResult(account=account, state=state, status=status)


class ApplicationList(CollectionResource):
    """Application resource list."""
    create_path = '/applications'
    resource_class = Application

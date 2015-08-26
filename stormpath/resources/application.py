"""Stormpath Application resource mappings."""

from datetime import datetime
from uuid import uuid4
try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode

from .base import (
    CollectionResource,
    DeleteMixin,
    DictMixin,
    Resource,
    SaveMixin,
    StatusMixin,
    AutoSaveMixin,
)
from .login_attempt import LoginAttemptList
from ..id_site import IdSiteCallbackResult
from ..nonce import Nonce
from .password_reset_token import PasswordResetTokenList


class Application(Resource, DeleteMixin, DictMixin, AutoSaveMixin, SaveMixin, StatusMixin):
    """Stormpath Application resource.

    More info in documentation:
    http://docs.stormpath.com/python/product-guide/#applications
    """

    SSO_ENDPOINT = "https://api.stormpath.com/sso"
    SSO_LOGOUT_ENDPOINT = SSO_ENDPOINT + "/logout"

    autosaves = ('custom_data',)
    writable_attrs = (
        'custom_data',
        'description',
        'name',
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
        from .group import GroupList
        from .tenant import Tenant
        from .api_key import ApiKeyList
        from .custom_data import CustomData
        from .verification_email import VerificationEmailList
        from .oauth_policy import OauthPolicy

        return {
            'custom_data': CustomData,
            'accounts': AccountList,
            'api_keys': ApiKeyList,
            'account_store_mappings': AccountStoreMappingList,
            'default_account_store_mapping': AccountStoreMapping,
            'default_group_store_mapping': AccountStoreMapping,
            'groups': GroupList,
            'login_attempts': LoginAttemptList,
            'oauth_policy': OauthPolicy,
            'password_reset_tokens': PasswordResetTokenList,
            'tenant': Tenant,
            'verification_emails': VerificationEmailList
        }

    def authenticate_account(self, login, password, expand=None,
            account_store=None):
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
            login, password, expand, account_store, app=self)

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

    def build_id_site_redirect_url(self, callback_uri, path=None, state=None, logout=False):
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

        :return: A URI to witch to redirect the user.
        """
        import jwt
        from oauthlib.common import to_unicode
        api_key_secret = self._client.auth.secret
        api_key_id = self._client.auth.id

        endpoint = self.SSO_LOGOUT_ENDPOINT if logout else self.SSO_ENDPOINT

        try:
            irt = uuid4().get_hex()
        except AttributeError:
            irt = uuid4().hex

        body = {
            'iat': datetime.utcnow(),
            'jti': irt,
            'iss': api_key_id,
            'sub': self.href,
            'cb_uri': callback_uri,
        }
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

    def handle_id_site_callback(self, url_response):
        """Handles the callback from the ID site.

        :param url_response: A string representing the full url (with it's params) to witch the
            ID redirected to.

        :return: A :class:`stormpath.id_site.IdSiteCallbackResult` object. Which holds the
            :class:`stormpath.resources.account.Account` object and the state (if any was passed
            along when creating the redirect uri).

       """
        try:
            from urlparse import urlparse
        except ImportError:
            from urllib.parse import urlparse

        import jwt
        try:
            jwt_response = urlparse(url_response).query.split('=')[1]
        except Exception:  # because we wan't to catch everything
            return None

        api_key_secret = self._client.auth.secret

        # validate signature
        try:
            decoded_data = jwt.decode(
                jwt_response, api_key_secret, audience=self._client.auth.id,
                algorithms=['HS256'])
        except (jwt.DecodeError, jwt.ExpiredSignature):
            return None

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
        return IdSiteCallbackResult(account=account, state=state, status=status)


class ApplicationList(CollectionResource):
    """Application resource list."""
    create_path = '/applications'
    resource_class = Application

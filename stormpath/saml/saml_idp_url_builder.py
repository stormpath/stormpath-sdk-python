try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode
from uuid import uuid4
from datetime import datetime
import jwt
from oauthlib.common import to_unicode


class SamlIdpUrlBuilder(object):

    def __init__(self, application):
        self.application = application

    def _get_service_provider(self):
        return self.application.saml_policy.service_provider

    def build(self, options=None):
        service_provider = self._get_service_provider()
        api_key_secret = self.application._client.auth.secret
        api_key_id = self.application._client.auth.id

        try:
            jti = uuid4().get_hex()
        except AttributeError:
            jti = uuid4().hex

        claims = {
            'iat': datetime.utcnow(),
            'jti': jti,
            'iss': api_key_id
        }

        if options:
            if 'cb_uri' in options:
                claims['cb_uri'] = options['cb_uri']

            if 'ash' in options:
                claims['ash'] = options['ash']

            if 'onk' in options:
                claims['onk'] = options['onk']

            if 'state' in options:
                claims['state'] = options['state']

        jwt_signature = to_unicode(
            jwt.encode(
                claims, api_key_secret, 'HS256', headers={'kid': api_key_id}),
            'UTF-8')
        url_params = {'accessToken': jwt_signature}
        sso_initiation_endpoint = service_provider.sso_initiation_endpoint.href

        encoded_params = urlencode(url_params)
        init_url = "%s?%s" % (sso_initiation_endpoint, encoded_params)

        return init_url

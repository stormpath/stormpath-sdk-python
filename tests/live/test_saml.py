import jwt
from stormpath.saml import SamlIdpUrlBuilder
from tests.live.base import AuthenticatedLiveBase


class TestSamlIdpUrlBuilder(AuthenticatedLiveBase):

    def setUp(self):
        super(TestSamlIdpUrlBuilder, self).setUp()

        self.app_name = self.get_random_name()
        self.app = self.client.applications.create({
            'name': self.app_name,
            'description': 'test app'
        })

    def test_build_default_url(self):
        saml_idp_url_builder = SamlIdpUrlBuilder(self.app)
        url = saml_idp_url_builder.build()

        self.assertTrue('accessToken' in url)

        token = url.split('accessToken=')[1]
        result = jwt.decode(token, self.app._client.auth.secret)

        self.assertTrue('iss' in result.keys())
        self.assertTrue('iat' in result.keys())
        self.assertTrue('jti' in result.keys())

    def test_build_uri_with_options(self):
        options = {
            'cb_uri': 'http://some_cb_uri.com/',
            'ash': 'ash',
            'onk': 'onk',
            'state': 'state'
        }

        saml_idp_url_builder = SamlIdpUrlBuilder(self.app)
        url = saml_idp_url_builder.build(options)

        self.assertTrue('accessToken' in url)

        token = url.split('accessToken=')[1]
        result = jwt.decode(token, self.app._client.auth.secret)

        self.assertTrue('cb_uri' in result.keys())
        self.assertTrue('ash' in result.keys())
        self.assertTrue('onk' in result.keys())
        self.assertTrue('state' in result.keys())

        self.assertEqual(result['cb_uri'], options['cb_uri'])
        self.assertEqual(result['ash'], options['ash'])
        self.assertEqual(result['onk'], options['onk'])
        self.assertEqual(result['state'], options['state'])

        # import pytest; pytest.set_trace()
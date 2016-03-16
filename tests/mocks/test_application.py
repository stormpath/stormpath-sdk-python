from unittest import TestCase
from stormpath.resources.password_reset_token import \
    PasswordResetToken, PasswordResetTokenList

try:
    from mock import MagicMock
except ImportError:
    from unittest.mock import MagicMock


class TestPasswordResetToken(TestCase):
    def setUp(self):
        super(TestPasswordResetToken, self).setUp()
        self.client = MagicMock(BASE_URL='http://example.com')

    def test_password_reset_tokens(self):
        tokens_href = 'http://example.com/tokens'
        token_string = 'I-AM-TOKEN'
        token_href = '%s/%s' % (tokens_href, token_string)

        token = PasswordResetToken(
            self.client, properties={'href': token_href})
        self.assertEqual(token.token, token_string)

        tokens = PasswordResetTokenList(self.client, href=tokens_href)
        href = tokens.build_reset_href(token)
        self.assertEqual(href, token_href)

"""Live tests of common resource functionality.

We can use (almost) any resource here - Account is a convenient choice.
"""

from stormpath.resources.base import Expansion

from .base import ApiKeyBase


class TestApiKeys(ApiKeyBase):

    def test_dict_mixin(self):
        _, acc = self.create_account(self.app.accounts)
        _, acc = self.create_account()
        api_key = self.create_api_key(acc)

        self.assertTrue('id' in api_key)
        self.assertTrue('secret' in api_key)

        k = self.app.api_keys.get_key(api_key.id)

        self.assertEqual(k.id, api_key.id)


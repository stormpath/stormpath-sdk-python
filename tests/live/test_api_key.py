"""Live tests of ApiKeyList and ApiKey."""

from tests.live.base import ApiKeyBase


class TestApiKey(ApiKeyBase):

    def test_create_api_key_with_name_and_description(self):
        _, account = self.create_account(self.app.accounts)

        name = 'key_name'
        description = 'some key description'

        api_key = account.api_keys.create({'name': name, 'description': description})

        self.assertEqual(api_key.name, name)
        self.assertEqual(api_key.description, description)

"""Live tests of basic AccountSchema functionality."""

from datetime import datetime

from .base import AccountBase


class TestAccountSchema(AccountBase):

    def test_account_schema_properties(self):
        schema = self.dir.account_schema

        self.assertTrue(schema.href)
        self.assertTrue(schema.created_at)
        self.assertTrue(schema.modified_at)
        self.assertTrue(schema.fields.href)
        self.assertIsInstance(schema.created_at, datetime)
        self.assertIsInstance(schema.modified_at, datetime)
        self.assertEqual(schema.directory.href, self.dir.href)

    def test_easy_import(self):
        try:
            from stormpath.resources import AccountSchema
        except Exception:
            self.fail('Could not import stormpath.resources.AccountSchema.')

"""Live tests of basic Field functionality."""

from datetime import datetime

from stormpath.error import Error

from .base import AccountBase


def TestFields(AccountBase):

    def test_fields_properties(self):
        fields = self.dir.account_schema.fields

        self.assertEqual(len(fields), 2)

        for field in fields:
            self.assertTrue(field.href)
            self.assertTrue(field.created_at)
            self.assertTrue(field.modified_at)
            self.assertIsInstance(field.created_at, datetime)
            self.assertIsInstance(field.modified_at, datetime)
            self.assertTrue(field.name)
            self.assertFalse(field.required)
            self.assertTrue(field.schema.href)

        for field in fields:
            field.required = True
            field.save()

        for field in fields:
            self.assertTrue(field.required)

    def test_fields_required(self):
        fields = self.dir.account_schema.fields

        acc = self.dir.accounts.create({
            'email': 'test@testmail.stormpath.com',
            'password': 'hIthereIL0V3C00kies!!',
        })

        self.assertEqual(acc.given_name, None)
        self.assertEqual(acc.surname, None)

        for field in fields:
            field.required = True
            field.svae()

        with self.assertRaises(Error):
            acc = self.dir.accounts.create({
                'email': 'test@testmail.stormpath.com',
                'password': 'hIthereIL0V3C00kies!!',
            })

        acc = self.dir.accounts.create({
            'given_name': 'Randall',
            'surname': 'Degges',
            'email': 'test@testmail.stormpath.com',
            'password': 'hIthereIL0V3C00kies!!',
        })

    def test_fields_search(self):
        fields = self.dir.account_schema.fields

        field = fields.search('givenName')[0]
        self.assertEqual(field.name, 'givenName')

        field = fields.search('surname')[0]
        self.assertEqual(field.name, 'surname')

    def test_easy_import(self):
        try:
            from stormpath.resources import Field
        except Exception:
            self.fail('Could not import stormpath.resources.Field.')

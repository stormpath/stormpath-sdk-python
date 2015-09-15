"""Test to assert functionality of our stormpath module."""


from unittest import TestCase


class TestObjectsAreAvailableForImport(TestCase):
    def test_can_import_client(self):
        from stormpath import Client
        from stormpath.client import Client as RawClient

        self.assertEqual(Client, RawClient)

    def test_can_import_Application(self):
        from stormpath import Application
        from stormpath.resources.application import Application as RawApplication

        self.assertEqual(Application, RawApplication)

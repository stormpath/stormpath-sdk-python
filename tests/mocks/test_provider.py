""""
Integration tests for various pieces involved in external provider support.
"""

from datetime import datetime
from dateutil.tz import tzutc
from unittest import TestCase, main

try:
    from mock import MagicMock
except ImportError:
    from unittest.mock import MagicMock

from stormpath.resources.account import Account
from stormpath.resources.application import Application
from stormpath.resources.directory import DirectoryList
from stormpath.resources.provider_data import ProviderData


class TestProviderAccounts(TestCase):

    def test_is_new_account_if_sp_http_status_is_201(self):
        ds = MagicMock()
        ds.get_resource.return_value = {
            'sp_http_status': 201
        }

        acc = Account(client=MagicMock(data_store=ds), href='test/account')
        is_new = acc.is_new_account

        ds.get_resource.assert_called_once_with('test/account', params=None)
        self.assertTrue(is_new)

    def test_is_not_new_account_if_sp_http_status_is_200(self):
        ds = MagicMock()
        ds.get_resource.return_value = {
            'sp_http_status': 200
        }

        acc = Account(client=MagicMock(data_store=ds), href='test/account')
        is_new = acc.is_new_account

        ds.get_resource.assert_called_once_with('test/account', params=None)
        self.assertFalse(is_new)

    def test_app_get_provider_acc_does_create_w_provider_data(self):
        ds = MagicMock()
        ds.get_resource.return_value = {}
        client = MagicMock(data_store=ds, BASE_URL='http://example.com')

        app = Application(client=client, properties={
            'href': 'test/app',
            'accounts': {'href': '/test/app/accounts'}
        })

        app.get_provider_account('myprovider', access_token='foo')

        ds.create_resource.assert_called_once_with(
            'http://example.com/test/app/accounts', {
                'providerData': {
                    'providerId': 'myprovider',
                    'accessToken': 'foo'
                }
            }, params={})


class TestProviderDirectories(TestCase):

    def test_creating_provider_directory_passes_provider_info(self):
        ds = MagicMock()
        ds.create_resource.return_value = {}

        dl = DirectoryList(
            client=MagicMock(data_store=ds, BASE_URL='http://example.com'),
            href='directories')

        dl.create({
            'name': 'Foo',
            'description': 'Desc',
            'provider': {
                'client_id': 'ID',
                'client_secret': 'SECRET',
                'redirect_uri': 'SOME_URL',
                'provider_id': 'myprovider'
            }
        })

        ds.create_resource.assert_called_once_with(
            'http://example.com/directories', {
                'description': 'Desc',
                'name': 'Foo',
                'provider': {
                    'clientSecret': 'SECRET',
                    'providerId': 'myprovider',
                    'redirectUri': 'SOME_URL',
                    'clientId': 'ID'
                }
            }, params={})


class TestProviderData(TestCase):

    def test_provider_data_get_exposed_readonly_timestamp_attrs(self):
        ds = MagicMock()
        created_and_modified_at = datetime(
            2015, 2, 26, 12, 0, 0 ,0, tzinfo=tzutc())
        ds.get_resource.return_value = {
            'created_at': '2015-02-26 12:00:00+00:00',
            'modified_at': '2015-02-26 12:00:00+00:00'
        }

        pd = ProviderData(
            client=MagicMock(data_store=ds, BASE_URL='http://example.com'),
            href='provider-data')

        self.assertEqual(pd.created_at, created_and_modified_at)
        self.assertEqual(pd['created_at'], created_and_modified_at)
        self.assertEqual(pd.modified_at, created_and_modified_at)
        self.assertEqual(pd['modified_at'], created_and_modified_at)

    def test_provider_data_modify_exposed_readonly_timestamp_attrs(self):
        ds = MagicMock()
        ds.get_resource.return_value = {
            'created_at': '2015-02-26 12:00:00+00:00',
            'modified_at': '2015-02-26 12:00:00+00:00'
        }

        pd = ProviderData(
            client=MagicMock(data_store=ds, BASE_URL='http://example.com'),
            href='provider-data')

        with self.assertRaises(AttributeError):
            pd.created_at = 'whatever'
        with self.assertRaises(AttributeError):
            pd['created_at'] = 'whatever'
        with self.assertRaises(AttributeError):
            pd.modified_at = 'whatever'
        with self.assertRaises(AttributeError):
            pd['modified_at'] = 'whatever'

        with self.assertRaises(Exception):
            del pd['created_at']
        with self.assertRaises(Exception):
            del pd['modified_at']


if __name__ == '__main__':
    main()

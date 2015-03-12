from unittest import TestCase, main

try:
    from mock import patch, MagicMock, PropertyMock, create_autospec
except ImportError:
    from unittest.mock import patch, MagicMock, PropertyMock, create_autospec

from stormpath.resources.account import Account
from stormpath.resources.directory import Directory
from stormpath.resources.group import Group, GroupList
from stormpath.resources.login_attempt import AuthenticationResult


class TestAccount(TestCase):
    def setUp(self):
        super(TestAccount, self).setUp()
        self.client = MagicMock(BASE_URL='http://example.com')
        self.account = Account(self.client,
                properties={
                    'href': 'http://example.com/account',
                    'username': 'username',
                    'given_name': 'given_name',
                    'surname': 'surname',
                    'email': 'test@example.com',
                    'password': 'Password123!'})
        ds = MagicMock()
        self.gs = GroupList(MagicMock(data_store=ds), href='test/collection')
        self.g = Group(self.client,
                properties={'href': 'http://example.com/group', 'name': 'group'})
        self.g2 = Group(self.client,
                properties={'href': 'http://example.com/group2', 'name': 'group2'})
        ds.get_resource.return_value = {'href': self.g.href, 'name': self.g.name}
        self.d = Directory(self.client,
                properties={'href': 'http://example.com/directory', 'name': 'directory'})
        self.d._set_properties({'groups': self.gs})
        self.account._set_properties({'directory': self.d})

    def test_account_str_method(self):
        self.assertEquals('username', self.account.__str__())

    def test_resolve_group_raises_type_error_on_invalid_arg_type(self):
        self.assertRaises(TypeError, self.account._resolve_group, 1234)

    def test_resolve_group_with_object(self):
        group = Group(self.client, properties={'name': 'name'})
        ret = self.account._resolve_group(group)
        self.assertEquals(group, ret)

    def test_resolve_group_with_href(self):
        ret = self.account._resolve_group('http://example.com/group')
        self.assertEquals(ret.name, self.g.name)

    def test_resolve_group_name(self):
        gs_ds = MagicMock()
        gs_ds.get_resource.return_value = {
            'href': 'test/collection',
            'offset': 0,
            'limit': 25,
            'items': [
                {'href': 'http://example.com/group', 'name': 'group'},
            ]
        }
        gs = GroupList(MagicMock(data_store=gs_ds), href='test/collection')
        d = Directory(self.client,
                properties={'href': 'http://example.com/directory', 'name': 'directory'})
        d._set_properties({'groups': gs})
        self.account._set_properties({'directory': d})
        ret = self.account._resolve_group('group')
        self.assertEquals(ret.href, self.g.href)

    def test_resolve_non_existent_group(self):
        gs_ds = MagicMock()
        gs_ds.get_resource.return_value = {
            'href': 'test/collection',
            'offset': 0,
            'limit': 25,
            'items': [
                {'href': 'http://example.com/group', 'name': 'group'},
            ]
        }
        gs = GroupList(MagicMock(data_store=gs_ds), href='test/collection')
        d = Directory(self.client,
                properties={'href': 'http://example.com/directory', 'name': 'directory'})
        d._set_properties({'groups': gs})
        self.account._set_properties({'directory': d})
        self.assertRaises(ValueError, self.account._resolve_group, 'non_existent')

    def test_add_account_to_group(self):
        self.account.add_group('http://example.com/group')
        self.account._client.group_memberships.create.assert_any_calls()

    def test_memership_for_single_group(self):
        gs_ds = MagicMock()
        gs_ds.get_resource.return_value = {
            'href': 'test/collection',
            'offset': 0,
            'limit': 25,
            'items': [
                {'href': 'http://example.com/group', 'name': 'group'},
                {'href': 'http://example.com/group2', 'name': 'group2'},
            ]
        }
        gs = GroupList(MagicMock(data_store=gs_ds), href='test/collection')
        GroupList.writable_attrs += ('query',)
        gs.query = lambda *args, **kwargs: [self.g]
        d = Directory(self.client,
                properties={'href': 'http://example.com/directory', 'name': 'directory'})
        d._set_properties({'groups': gs})
        self.account._set_properties({'directory': d, 'groups': gs})
        self.assertTrue(self.account.has_group('group'))

    def test_login_attempt(self):
        app = MagicMock()
        app.accounts.get.return_value = self.account
        app._client.auth.secret = 'fakeApiKeyProperties.secret'
        app.href = 'http://example.com/application'

        ar = AuthenticationResult(
            client=self.client,
            properties={'account': self.account, 'application': app})
        at = ar.get_access_token()

        self.assertEqual(self.account, at.account)
        self.assertEqual(app, at.app)
        self.assertFalse(at.for_api_key)


if __name__ == '__main__':
    main()


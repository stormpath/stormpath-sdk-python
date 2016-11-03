from unittest import TestCase, main
from stormpath.error import Error as StormpathError
from stormpath.resources import GroupMembershipList, GroupMembership
from stormpath.resources.account_store import AccountStore
from stormpath.resources.api_key import ApiKeyList

try:
    from mock import MagicMock
except ImportError:
    from unittest.mock import MagicMock

from stormpath.resources.account import Account, AccountList
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
                    'email': 'test@testmail.stormpath.com',
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
        self.g._set_properties({'directory': self.d})

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
        ds = MagicMock()
        self.acs = AccountList(MagicMock(data_store=ds), href='test/accounts')
        self.d._set_properties({'accounts': self.acs})
        ds.get_resource.return_value = {
            'href': self.account.href, 'username': self.account.username
        }

        self.g.add_account('http://example.com/account')
        args, _ = self.account._client.group_memberships.create.call_args
        self.assertEqual(args[0]['account'].href, self.account.href)
        self.assertEqual(args[0]['group'].href, self.g.href)

    def test_add_account_to_group_by_username(self):
        ds = MagicMock()
        self.acs = AccountList(MagicMock(data_store=ds), href='test/accounts')
        self.d._set_properties({'accounts': self.acs})
        ds.get_resource.return_value = {
            'href': 'test/accounts',
            'offset': 0,
            'limit': 25,
            'items': [
                {'href': self.account.href, 'username': self.account.username}
            ],
        }

        self.g.add_account(self.account.username)
        args, _ = self.account._client.group_memberships.create.call_args
        self.assertEqual(args[0]['account'].href, self.account.href)
        self.assertEqual(args[0]['group'].href, self.g.href)

    def test_add_account_to_group_by_search_dict(self):
        ds = MagicMock()
        self.acs = AccountList(MagicMock(data_store=ds), href='test/accounts')
        self.d._set_properties({'accounts': self.acs})
        ds.get_resource.return_value = {
            'href': 'test/accounts',
            'offset': 0,
            'limit': 25,
            'items': [
                {'href': self.account.href, 'username': self.account.username}
            ],
        }

        self.g.add_account({'username': self.account.username})
        args, _ = self.account._client.group_memberships.create.call_args
        self.assertEqual(args[0]['account'].href, self.account.href)
        self.assertEqual(args[0]['group'].href, self.g.href)

    def test_add_accounts_to_group(self):
        account2 = Account(
            self.client,
            properties={
                'href': 'http://example.com/account2',
                'username': 'username2',
                'given_name': 'given_name',
                'surname': 'surname',
                'email': 'test2@testmail.stormpath.com',
                'password': 'Password123!'
            })
        ds = MagicMock()
        self.acs = AccountList(MagicMock(data_store=ds), href='test/accounts')
        self.d._set_properties({'accounts': self.acs})
        ds.get_resource.return_value = {
            'href': self.account.href, 'username': self.account.username
        }

        self.g.add_accounts(['http://example.com/account', account2])
        self.assertEqual(
            self.account._client.group_memberships.create.call_count, 2)
        calls = self.account._client.group_memberships.create.call_args_list
        args, _ = calls[0]
        self.assertEqual(args[0]['account'].href, self.account.href)
        self.assertEqual(args[0]['group'].href, self.g.href)
        args, _ = calls[1]
        self.assertEqual(args[0]['account'].href, account2.href)
        self.assertEqual(args[0]['group'].href, self.g.href)

    def test_remove_account_from_group(self):
        ds = MagicMock()
        self.acs = AccountList(MagicMock(data_store=ds), href='test/accounts')
        self.d._set_properties({'accounts': self.acs})
        ds.get_resource.return_value = {
            'href': self.account.href, 'username': self.account.username
        }

        ds = MagicMock()
        ams = GroupMembershipList(
            MagicMock(data_store=ds), href='test/memberships')
        gm = GroupMembership(
            self.client,
            properties={
                'href': 'test/group-membership', 'account': self.account,
                'group': self.g
            })
        ds.get_resource.return_value = {
            'items': [gm], 'offset': 0, 'limit': 0
        }
        self.g._set_properties({'account_memberships': ams})
        self.g.remove_account(self.account.href)
        args, _ = gm._client.data_store.delete_resource.call_args
        self.assertEqual(args[0], gm.href)

    def test_remove_account_from_group_account_is_not_in(self):
        ds = MagicMock()
        self.acs = AccountList(MagicMock(data_store=ds), href='test/accounts')
        self.d._set_properties({'accounts': self.acs})
        ds.get_resource.return_value = {
            'href': self.account.href, 'username': self.account.username
        }

        ds = MagicMock()
        ams = GroupMembershipList(
            MagicMock(data_store=ds), href='test/memberships')
        ds.get_resource.return_value = {
            'items': [], 'offset': 0, 'limit': 0
        }
        self.g._set_properties({'account_memberships': ams})

        self.assertRaises(
            StormpathError, self.g.remove_account, 'http://example.com/account')

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

    def test_valid_account_store(self):
        directory = Directory(
            self.client,
            properties={
                'href': 'http://example.com/directories/dir',
                'name': 'directory'
            })

        account_store = AccountStore(
            client=self.client, properties={'href': directory.href})
        self.assertEqual(account_store.href, directory.href)
        self.assertEqual(type(account_store), type(directory))

    def test_invalid_account_store(self):
        self.assertRaises(ValueError, AccountStore, [self.client])
        self.assertRaises(
            ValueError, AccountStore, [self.client, '/wrong/href'])


class TestAccountApiKey(TestAccount):
    def setUp(self):
        super(TestAccountApiKey, self).setUp()
        self.ak_ds = MagicMock()
        ak_client = MagicMock(
            BASE_URL='http://example.com', data_store=self.ak_ds)
        aks = ApiKeyList(ak_client, href='http://example.com/api-keys')
        self.account._set_properties({'api_keys': aks})

        self.href = 'http://example.com/api-key'
        self.id = '123'
        self.secret = 'SECRET'
        self.ak_ds.create_resource.return_value = {
            'href': self.href, 'id': self.id, 'secret': self.secret
        }

    def test_create_api_key(self):
        api_key = self.account.api_keys.create()

        self.assertEqual(api_key.href, self.href)
        self.assertEqual(api_key.id, self.id)
        self.assertEqual(api_key.secret, self.secret)

    def test_get_api_key_by_id(self):
        api_key = self.account.api_keys.create()

        self.ak_ds.get_resource.return_value = {
            'items': [
                {'href': self.href, 'id': self.id, 'secret': self.secret}
            ]
        }
        ak = self.account.api_keys.get_key(client_id=self.id)
        self.assertEqual(ak.href, api_key.href)

    def test_get_api_key_by_non_existent_id(self):
        self.ak_ds.get_resource.return_value = {'items': []}
        ak = self.account.api_keys.get_key(client_id='i-dont-exist')
        self.assertFalse(ak)

    def test_get_api_key_by_id_and_secret(self):
        api_key = self.account.api_keys.create()

        self.ak_ds.get_resource.return_value = {
            'items': [
                {'href': self.href, 'id': self.id, 'secret': self.secret}
            ]
        }
        ak = self.account.api_keys.get_key(
            client_id=self.id, client_secret=self.secret)
        self.assertEqual(ak.href, api_key.href)

    def test_get_api_key_by_id_and_wrong_secret(self):
        self.account.api_keys.create()

        self.ak_ds.get_resource.return_value = {
            'items': [
                {'href': self.href, 'id': self.id, 'secret': self.secret}
            ]
        }
        ak = self.account.api_keys.get_key(
            client_id=self.id, client_secret='WRONG-SECRET')
        self.assertFalse(ak)


if __name__ == '__main__':
    main()

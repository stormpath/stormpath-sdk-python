"""Live tests of common resource functionality.

We can use (almost) any resource here - Account is a convenient choice.
"""
import jwt
from time import sleep

from stormpath.cache.entry import CacheEntry
from stormpath.resources.base import Expansion

from .base import AccountBase
from .base import ApiKeyBase



class TestResource(AccountBase):

    def test_dict_mixin(self):
        _, acc = self.create_account(self.app.accounts)

        self.assertEqual(acc['username'], acc.username)
        self.assertTrue('username' in acc)
        self.assertFalse('nonexistent' in acc)

        acc['given_name'] = 'Updated Given Name'
        acc.update({
            'surname': 'Updated Surname'
        })

        acc = self.app.accounts.get(acc.href)

        self.assertEqual(acc.given_name, 'Updated Given Name')
        self.assertEqual(acc.surname, 'Updated Surname')

        self.assertTrue('username' in acc.keys())
        self.assertTrue(acc.username in acc.values())
        self.assertTrue(('username', acc.username) in acc.items())

    def test_status_mixin(self):
        _, acc = self.create_account(self.app.accounts)

        self.assertTrue(acc.is_enabled())
        self.assertFalse(acc.is_disabled())

        acc.status = acc.STATUS_DISABLED
        acc.save()

        acc = self.app.accounts.get(acc.href)

        self.assertFalse(acc.is_enabled())
        self.assertTrue(acc.is_disabled())

    def test_cache_entry_to_dict_parse(self):
        _, acc = self.create_account(self.app.accounts)
        acc.update({'surname': 'Surname'})

        acc_entry_before = acc._store._get_cache(acc.href).store[acc.href]
        acc_entry_after = CacheEntry.parse(acc_entry_before.to_dict())
        self.assertEqual(acc_entry_before.value, acc_entry_after.value)
        self.assertEqual(
            acc_entry_before.created_at, acc_entry_after.created_at)
        self.assertEqual(
            acc_entry_before.last_accessed_at,
            acc_entry_after.last_accessed_at)

    def test_created_and_modified_at(self):
        _, acc = self.create_account(self.app.accounts)
        created_at_before, modified_at_before = acc.created_at, acc.modified_at

        sleep(1)
        acc.update({'surname': 'Surname'})
        created_at_after, modified_at_after = acc.created_at, acc.modified_at

        self.assertEqual(created_at_before, created_at_after)
        self.assertTrue(modified_at_before < modified_at_after)

        with self.assertRaises(AttributeError):
            acc.update({'created_at': 'whatever'})


class TestCollectionResource(AccountBase):

    def setUp(self):
        super(TestCollectionResource, self).setUp()
        self.accounts = []
        for i in range(5):
            _, acc = self.create_account(self.app.accounts,
                given_name='Test', surname='Account')
            self.accounts.append(acc)

    def test_iteration(self):
        accounts = []
        for acc in self.app.accounts:
            accounts.append(acc)

        self.assertEqual(
            {acc.href for acc in self.accounts},
            {acc.href for acc in accounts}
        )

    def test_sorting(self):
        self.assertEqual(
            [acc.href for acc in self.app.accounts.order('email desc')],
            [acc.href for acc in sorted(self.accounts,
                key=lambda acc: acc.email, reverse=True)]
        )

    def test_search(self):
        accs = self.app.accounts.search({
            'given_name': 'Test',
            'surname': 'Account'
        })
        self.assertEqual(
            {acc.href for acc in accs},
            {acc.href for acc in self.accounts})

        accs = self.app.accounts.search('ccount')
        self.assertEqual(
            {acc.href for acc in accs},
            {acc.href for acc in self.accounts})

        accs = self.app.accounts.search(
            {'username': self.accounts[0].username})
        self.assertTrue(len(accs), 1)
        self.assertEqual(accs[0].href, self.accounts[0].href)

    def test_search_datetime(self):
        earliest_created_at = self.app.accounts.order(
            'created_at')[0].created_at
        latest_created_at = self.app.accounts.order(
            'created_at desc')[0].created_at

        self.assertEqual(
            len(self.app.accounts.search({'created_at': '[,2015-01-01]'})), 0)
        self.assertEqual(
            len(self.app.accounts.search({'created_at': '[2015-01-01,]'})), 5)
        self.assertEqual(
            len(self.app.accounts.search({'created_at': '[%s,%s]' % (
                earliest_created_at.isoformat(),
                latest_created_at.isoformat())})),
            5)
        self.assertTrue(
            len(self.app.accounts.search(
                {'created_at': earliest_created_at.isoformat()})) > 0)

    def test_pagination(self):
        page1 = self.app.accounts.order('username asc')[:2]
        page2 = self.app.accounts.order('username asc')[2:4]
        page3 = self.app.accounts.order('username asc')[4:100]
        all_but_first = self.app.accounts.order('username asc')[1:]

        self.assertEqual(len(page1), 2)
        self.assertEqual(len(page2), 2)
        self.assertEqual(len(page3), len(self.accounts) - 4)
        self.assertEqual(len(all_but_first), len(self.accounts) - 1)

        accs = []
        for acc in page1:
            accs.append(acc.href)
        for acc in page2:
            accs.append(acc.href)
        for acc in page3:
            accs.append(acc.href)

        self.assertEqual(accs, [acc.href for acc in
            sorted(self.accounts, key=lambda acc: acc.username)])

    def test_expansion(self):
        expansion = Expansion()
        expansion.add_property('accounts', offset=0, limit=3)
        dir = self.client.directories.get(self.dir.href, expansion)
        self.assertEqual(len(dir.accounts), 5)

    def test_href_indexing(self):
        href = self.accounts[0].href
        acc = self.app.accounts[href]

        self.assertEqual(self.accounts[0].username, acc.username)


class TestApiKeys(ApiKeyBase):

    def test_api_key_resource_gets_built_properly_and_cached(self):
        _, acc = self.create_account(self.app.accounts)
        api_key = self.create_api_key(acc)

        self.assertTrue('id' in api_key.__dict__)
        self.assertTrue('secret' in api_key.__dict__)

        k = self.app.api_keys.get_key(api_key.id)

        self.assertEqual(k.id, api_key.id)

        k = self.app.api_keys.get_key(api_key.id, client_secret=api_key.secret)
        self.assertEqual(k.secret, api_key.secret)

    def test_wrong_secret_with_get_key_method(self):
        _, acc = self.create_account(self.app.accounts)
        api_key = self.create_api_key(acc)

        self.assertTrue('id' in api_key.__dict__)
        self.assertTrue('secret' in api_key.__dict__)

        k = self.app.api_keys.get_key(api_key.id, client_secret='INVALID_SECRET')
        self.assertFalse(k)


class TestIdSite(ApiKeyBase):

    def test_building_id_site_redirect_uri(self):
        try:
            from urlparse import urlparse
        except ImportError:
            from urllib.parse import urlparse

        ret = self.app.build_id_site_redirect_url('http://localhost/')
        try:
            jwt_response = urlparse(ret).query.split('=')[1]
        except:
            self.fail("Failed to parse ID site redirect uri")

        try:
            decoded_data = jwt.decode(jwt_response, verify=False)
        except jwt.DecodeError:
            self.fail("Invaid JWT generated.")

        self.assertIsNotNone(decoded_data.get('iat'))
        self.assertIsNotNone(decoded_data.get('jti'))
        self.assertIsNotNone(decoded_data.get('iss'))
        self.assertEqual(decoded_data.get('iss'), self.app._client.auth.id)
        self.assertIsNotNone(decoded_data.get('sub'))
        self.assertIsNotNone(decoded_data.get('cb_uri'))
        self.assertEqual(decoded_data.get('cb_uri'), 'http://localhost/')
        self.assertIsNone(decoded_data.get('path'))
        self.assertIsNone(decoded_data.get('state'))


        ret = self.app.build_id_site_redirect_url(
                'http://testserver/',
                path='/#/register',
                state='test')
        try:
            jwt_response = urlparse(ret).query.split('=')[1]
        except:
            self.fail("Failed to parse ID site redirect uri")

        try:
            decoded_data = jwt.decode(jwt_response, verify=False)
        except jwt.DecodeError:
            self.fail("Invaid JWT generated.")

        self.assertEqual(decoded_data.get('path'), '/#/register')
        self.assertEqual(decoded_data.get('state'), 'test')


    def test_id_site_callback_handler(self):
        from uuid import uuid4
        import datetime
        import jwt
        from oauthlib.common import to_unicode

        _, acc = self.create_account(self.app.accounts)
        now = datetime.datetime.utcnow()

        try:
            irt = uuid4().get_hex()
        except AttributeError:
            irt = uuid4().hex

        fake_jwt_data = {
                'exp': now + datetime.timedelta(seconds=3600),
                'aud': self.app._client.auth.id,
                'irt': irt,
                'iss': 'Stormpath',
                'sub': acc.href,
                'isNewSub': False,
                'state': None,
        }

        fake_jwt = to_unicode(jwt.encode(
            fake_jwt_data,
            self.app._client.auth.secret,
            'HS256'), 'UTF-8')
        fake_jwt_response = 'http://localhost/?jwtResponse=%s' % fake_jwt
        ret = self.app.handle_id_site_callback(fake_jwt_response)
        self.assertIsNotNone(ret)
        self.assertEqual(ret.account.href, acc.href)
        self.assertIsNone(ret.state)

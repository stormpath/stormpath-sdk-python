"""Live tests of common resource functionality.

We can use (almost) any resource here - Account is a convenient choice.
"""

from stormpath.resources.base import Expansion

from .base import AccountBase


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
        self.assertEqual(len(dir.accounts), 3)

    def test_href_indexing(self):
        href = self.accounts[0].href
        acc = self.app.accounts[href]

        self.assertEqual(self.accounts[0].username, acc.username)


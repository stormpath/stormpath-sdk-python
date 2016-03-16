from datetime import datetime

from .base import SingleApplicationBase, AccountBase

CUSTOM_DATA = {
    'foo': 'F00!',
    'foo_val': 1,
    'fooCamelCase': True,
    'list_of_foo': [
        'a', 1, False, {
            'bar': 1,
            'bar_val': 'value of bar',
            'barCamelCase': True,
            'subBar': {
                'sub_bar_name': 'Baz',
                'subBarCamel': 'Quux'
            }
        }
    ]
}


def remove_timestamp_attrs(custom_data):
    remaining_keys = set(custom_data) - set(
        custom_data.exposed_readonly_timestamp_attrs)
    return {k: custom_data[k] for k in remaining_keys}


class CustomDataTest(SingleApplicationBase):
    def setUp(self):
        super(CustomDataTest, self).setUp()
        self.custom_data_resources = {
                'applications': self.client.applications,
                'directories': self.client.directories
        }


class TestAccountCustomData(AccountBase):

    def test_account_creation_with_custom_data(self):
        _, acc = self.create_account(self.app.accounts,
            custom_data=CUSTOM_DATA)

        acc = self.app.accounts.get(acc.href)
        self.assertEqual(
            CUSTOM_DATA,
            remove_timestamp_attrs(acc.custom_data))
        self.assertTrue(
            set(acc.custom_data.exposed_readonly_timestamp_attrs).issubset(
                set(acc.custom_data.keys())))

    def test_custom_data_behaves_as_dict(self):
        _, acc = self.create_account(self.app.accounts,
            custom_data=CUSTOM_DATA)

        exposed_timestamps = acc.custom_data.exposed_readonly_timestamp_attrs

        self.assertEqual(
            set(list(CUSTOM_DATA.keys()) + list(exposed_timestamps)),
            set(acc.custom_data.keys()))

        self.assertEqual(
            len(CUSTOM_DATA.values()) + len(exposed_timestamps),
            len(acc.custom_data.values()))

        self.assertEqual(
            len(CUSTOM_DATA.items()) + len(exposed_timestamps),
            len(acc.custom_data.items()))

        self.assertEqual(
            set(CUSTOM_DATA) | set(exposed_timestamps),
            set(acc.custom_data))

        self.assertEqual(acc.custom_data['foo'], CUSTOM_DATA['foo'])
        self.assertEqual(acc.custom_data.get('foo'), CUSTOM_DATA['foo'])
        self.assertEqual(
            acc.custom_data.get('created_at'), acc.custom_data.created_at)
        self.assertIsInstance(acc.custom_data.created_at, datetime)
        self.assertEqual(
            acc.custom_data.get('modified_at'), acc.custom_data.modified_at)
        self.assertIsInstance(acc.custom_data.modified_at, datetime)
        self.assertEqual(acc.custom_data.get('nonexistent', 42), 42)

    def test_custom_data_modification(self):
        _, acc = self.create_account(self.app.accounts)

        self.assertEqual(
            set(acc.custom_data),
            set(acc.custom_data.exposed_readonly_timestamp_attrs))

        acc.custom_data['foo'] = 'F00!'
        acc.custom_data['bar_value'] = 1
        acc.custom_data['bazCamelCase'] = {'a': 1}

        acc.save()

        acc = self.app.accounts.get(acc.href)

        self.assertEqual(acc.custom_data['foo'], 'F00!')
        self.assertEqual(acc.custom_data['bar_value'], 1)
        self.assertEqual(acc.custom_data['bazCamelCase']['a'], 1)

        with self.assertRaises(KeyError):
            acc.custom_data['href'] = 'whatever'
        with self.assertRaises(KeyError):
            acc.custom_data['-foo'] = 'whatever'
        with self.assertRaises(KeyError):
            acc.custom_data['created_at'] = 'whatever'
        with self.assertRaises(KeyError):
            acc.custom_data['modified_at'] = 'whatever'

        acc.custom_data['foo'] = 'Not Foo anymore!'
        del acc.custom_data['bar_value']

        acc.custom_data.save()

        acc = self.app.accounts.get(acc.href)

        self.assertEqual(acc.custom_data['foo'], 'Not Foo anymore!')
        self.assertFalse('bar_value' in acc.custom_data)

        del acc.custom_data['foo']
        del acc.custom_data['bazCamelCase']

        acc.custom_data.save()

        acc = self.app.accounts.get(acc.href)

        with self.assertRaises(KeyError):
            del acc.custom_data['created_at']
        with self.assertRaises(KeyError):
            del acc.custom_data['modified_at']

        self.assertEqual(
            set(acc.custom_data),
            set(acc.custom_data.exposed_readonly_timestamp_attrs))

    def test_custom_data_set_as_dict(self):
        name, acc = self.create_account(self.app.accounts)

        self.assertEqual(
            set(acc.custom_data),
            set(acc.custom_data.exposed_readonly_timestamp_attrs))

        acc.custom_data = CUSTOM_DATA
        acc.save()

        acc = self.app.accounts.get(acc.href)

        self.assertEqual(acc.custom_data['foo'], 'F00!')
        self.assertEqual(acc.custom_data['foo_val'], 1)
        self.assertEqual(acc.custom_data['fooCamelCase'], True)
        self.assertEqual(acc.custom_data['list_of_foo'][0], 'a')


class TestApplicationAndDirectoryCustomData(CustomDataTest):

    def test_creation_with_custom_data(self):
        for e in self.custom_data_resources.values():
            res = e.create({'name': self.get_random_name(),
                'custom_data': CUSTOM_DATA})
            self.deletes.append(res)

            res = e.get(res.href)
            self.assertEqual(
                CUSTOM_DATA,
                remove_timestamp_attrs(res.custom_data))
            self.assertTrue(
                set(res.custom_data.exposed_readonly_timestamp_attrs).issubset(
                    set(res.custom_data.keys())))

    def test_custom_data_behaves_as_dict(self):
        for e in self.custom_data_resources.values():
            res = e.create({'name': self.get_random_name(),
                'custom_data': CUSTOM_DATA})
            exposed_timestamps = \
                res.custom_data.exposed_readonly_timestamp_attrs
            self.deletes.append(res)

            self.assertEqual(
                set(list(CUSTOM_DATA.keys()) + list(exposed_timestamps)),
                set(res.custom_data.keys()))

            self.assertEqual(
                len(CUSTOM_DATA.values()) + len(exposed_timestamps),
                len(res.custom_data.values()))

            self.assertEqual(
                len(CUSTOM_DATA.items()) + len(exposed_timestamps),
                len(res.custom_data.items()))

            self.assertEqual(
                set(CUSTOM_DATA) | set(exposed_timestamps),
                set(res.custom_data))

            self.assertEqual(res.custom_data['foo'], CUSTOM_DATA['foo'])
            self.assertEqual(res.custom_data.get('foo'), CUSTOM_DATA['foo'])
            self.assertEqual(res.custom_data.get('nonexistent', 42), 42)
            self.assertEqual(
                res.custom_data.get('created_at'),
                res.custom_data.created_at)
            self.assertIsInstance(res.custom_data.created_at, datetime)
            self.assertEqual(
                res.custom_data.get('modified_at'),
                res.custom_data.modified_at)
            self.assertIsInstance(res.custom_data.modified_at, datetime)

    def test_custom_data_modification(self):
        for e in self.custom_data_resources.values():
            res = e.create({'name': self.get_random_name()})
            self.deletes.append(res)

            self.assertEqual(
                set(res.custom_data),
                set(res.custom_data.exposed_readonly_timestamp_attrs))

            res.custom_data['foo'] = 'F00!'
            res.custom_data['bar_value'] = 1
            res.custom_data['bazCamelCase'] = {'a': 1}

            res.save()

            res = e.get(res.href)

            self.assertEqual(res.custom_data['foo'], 'F00!')
            self.assertEqual(res.custom_data['bar_value'], 1)
            self.assertEqual(res.custom_data['bazCamelCase']['a'], 1)

            with self.assertRaises(KeyError):
                res.custom_data['href'] = 'whatever'
            with self.assertRaises(KeyError):
                res.custom_data['-foo'] = 'whatever'
            with self.assertRaises(KeyError):
                res.custom_data['created_at'] = 'whatever'
            with self.assertRaises(KeyError):
                res.custom_data['modified_at'] = 'whatever'

            res.custom_data['foo'] = 'Not Foo anymore!'
            del res.custom_data['bar_value']

            res.custom_data.save()

            res = e.get(res.href)

            self.assertEqual(res.custom_data['foo'], 'Not Foo anymore!')
            self.assertFalse('bar_value' in res.custom_data)

            del res.custom_data['foo']
            del res.custom_data['bazCamelCase']

            res.custom_data.save()

            res = e.get(res.href)

            with self.assertRaises(KeyError):
                del res.custom_data['created_at']
            with self.assertRaises(KeyError):
                del res.custom_data['modified_at']

            self.assertEqual(
                set(res.custom_data),
                set(res.custom_data.exposed_readonly_timestamp_attrs))


class TestGroupCustomData(SingleApplicationBase):

    def test_creation_with_custom_data(self):

        res = self.app.groups.create({'name': self.get_random_name(),
            'custom_data': CUSTOM_DATA})

        res = self.app.groups.get(res.href)
        self.assertEqual(
            CUSTOM_DATA,
            remove_timestamp_attrs(res.custom_data))
        self.assertTrue(
            set(res.custom_data.exposed_readonly_timestamp_attrs).issubset(
                set(res.custom_data.keys())))

    def test_custom_data_behaves_as_dict(self):
        res = self.app.groups.create({'name': self.get_random_name(),
            'custom_data': CUSTOM_DATA})

        exposed_timestamps = res.custom_data.exposed_readonly_timestamp_attrs

        self.assertEqual(
            set(list(CUSTOM_DATA.keys()) + list(exposed_timestamps)),
            set(res.custom_data.keys()))

        self.assertEqual(
            len(CUSTOM_DATA.values()) + len(exposed_timestamps),
            len(res.custom_data.values()))

        self.assertEqual(
            len(CUSTOM_DATA.items()) + len(exposed_timestamps),
            len(res.custom_data.items()))

        self.assertEqual(
            set(CUSTOM_DATA) | set(exposed_timestamps),
            set(res.custom_data))

        self.assertEqual(res.custom_data['foo'], CUSTOM_DATA['foo'])
        self.assertEqual(res.custom_data.get('foo'), CUSTOM_DATA['foo'])
        self.assertEqual(res.custom_data.get('nonexistent', 42), 42)
        self.assertEqual(
            res.custom_data.get('created_at'),
            res.custom_data.created_at)
        self.assertIsInstance(res.custom_data.created_at, datetime)
        self.assertEqual(
            res.custom_data.get('modified_at'),
            res.custom_data.modified_at)
        self.assertIsInstance(res.custom_data.modified_at, datetime)

    def test_custom_data_modification(self):
        res = self.app.groups.create({'name': self.get_random_name()})

        self.assertEqual(
            set(res.custom_data),
            set(res.custom_data.exposed_readonly_timestamp_attrs))

        res.custom_data['foo'] = 'F00!'
        res.custom_data['bar_value'] = 1
        res.custom_data['bazCamelCase'] = {'a': 1}

        res.save()

        res = self.app.groups.get(res.href)

        self.assertEqual(res.custom_data['foo'], 'F00!')
        self.assertEqual(res.custom_data['bar_value'], 1)
        self.assertEqual(res.custom_data['bazCamelCase']['a'], 1)

        with self.assertRaises(KeyError):
            res.custom_data['href'] = 'whatever'
        with self.assertRaises(KeyError):
            res.custom_data['-foo'] = 'whatever'
        with self.assertRaises(KeyError):
            res.custom_data['created_at'] = 'whatever'
        with self.assertRaises(KeyError):
            res.custom_data['modified_at'] = 'whatever'

        res.custom_data['foo'] = 'Not Foo anymore!'
        del res.custom_data['bar_value']

        res.custom_data.save()

        res = self.app.groups.get(res.href)

        self.assertEqual(res.custom_data['foo'], 'Not Foo anymore!')
        self.assertFalse('bar_value' in res.custom_data)

        del res.custom_data['foo']
        del res.custom_data['bazCamelCase']

        res.custom_data.save()

        res = self.app.groups.get(res.href)

        with self.assertRaises(KeyError):
            del res.custom_data['created_at']
        with self.assertRaises(KeyError):
            del res.custom_data['modified_at']

        self.assertEqual(
            set(res.custom_data),
            set(res.custom_data.exposed_readonly_timestamp_attrs))


class TestTenantCustomData(SingleApplicationBase):

    def setUp(self):
        super(TestTenantCustomData, self).setUp()
        self.client.tenant.custom_data.delete()
        self.exposed_timestamps = \
            self.client.tenant.custom_data.exposed_readonly_timestamp_attrs

    def tearDown(self):
        super(TestTenantCustomData, self).tearDown()
        self.client.tenant.custom_data.delete()

    def test_tenant_has_custom_data_with_exposed_timestamp_attrs(self):
        self.assertEqual(
            set(self.client.tenant.custom_data),
            set(self.exposed_timestamps))

    def test_tenant_with_custom_data(self):
        self.client.tenant.custom_data['testCamelCase'] = 'TEST'
        self.client.tenant.save()
        self.assertEqual(
            {'testCamelCase': 'TEST'},
            remove_timestamp_attrs(self.client.tenant.custom_data))
        self.assertTrue(
            set(self.client.tenant.custom_data.
                exposed_readonly_timestamp_attrs).issubset(
                set(self.client.tenant.custom_data.keys())))

    def test_custom_data_behaves_as_dict(self):
        res = self.client.tenant
        exposed_timestamps = res.custom_data.exposed_readonly_timestamp_attrs

        for key in CUSTOM_DATA.keys():
            res.custom_data[key] = CUSTOM_DATA[key]

        self.assertEqual(
            set(list(CUSTOM_DATA.keys()) + list(exposed_timestamps)),
            set(res.custom_data.keys()))

        self.assertEqual(
            len(CUSTOM_DATA.values()) + len(exposed_timestamps),
            len(res.custom_data.values()))

        self.assertEqual(
            len(CUSTOM_DATA.items()) + len(exposed_timestamps),
            len(res.custom_data.items()))

        self.assertEqual(
            set(CUSTOM_DATA) | set(self.exposed_timestamps),
            set(res.custom_data))

        self.assertEqual(res.custom_data['foo'], CUSTOM_DATA['foo'])
        self.assertEqual(res.custom_data.get('foo'), CUSTOM_DATA['foo'])
        self.assertEqual(res.custom_data.get('nonexistent', 42), 42)

    def test_custom_data_modification(self):
        res = self.client.tenant
        self.assertEqual(set(res.custom_data), set(self.exposed_timestamps))

        for key in CUSTOM_DATA.keys():
            res.custom_data[key] = CUSTOM_DATA[key]

        res.custom_data['foo'] = 'F00!'
        res.custom_data['bar_value'] = 1
        res.custom_data['bazCamelCase'] = {'a': 1}

        res.save()

        self.assertEqual(res.custom_data['foo'], 'F00!')
        self.assertEqual(res.custom_data['bar_value'], 1)
        self.assertEqual(res.custom_data['bazCamelCase']['a'], 1)

        with self.assertRaises(KeyError):
            res.custom_data['href'] = 'whatever'
        with self.assertRaises(KeyError):
            res.custom_data['-foo'] = 'whatever'
        with self.assertRaises(KeyError):
            res.custom_data['created_at'] = 'whatever'
        with self.assertRaises(KeyError):
            res.custom_data['modified_at'] = 'whatever'

        res.custom_data['foo'] = 'Not Foo anymore!'
        del res.custom_data['bar_value']

        res.custom_data.save()

        self.assertEqual(res.custom_data['foo'], 'Not Foo anymore!')
        self.assertFalse('bar_value' in res.custom_data)

        del res.custom_data['foo']
        del res.custom_data['foo_val']
        del res.custom_data['list_of_foo']
        del res.custom_data['fooCamelCase']
        del res.custom_data['bazCamelCase']

        res.custom_data.save()

        with self.assertRaises(KeyError):
            del res.custom_data['created_at']
        with self.assertRaises(KeyError):
            del res.custom_data['modified_at']

        res = self.client.tenant

        self.assertEqual(set(res.custom_data), set(self.exposed_timestamps))

    def test_custom_data_deletion(self):
        res = self.client.tenant
        self.assertEqual(set(res.custom_data), set(self.exposed_timestamps))

        for key in CUSTOM_DATA.keys():
            res.custom_data[key] = CUSTOM_DATA[key]

        self.client.tenant.custom_data.delete()
        assert set(res.custom_data) == set(self.exposed_timestamps)

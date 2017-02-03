"""Live tests of CustomData functionality."""


from datetime import datetime
from unittest import TestCase

try:
    from mock import MagicMock, patch
except ImportError:
    from unittest.mock import MagicMock, patch

from dateutil.tz import tzutc, tzoffset
from stormpath.resources.base import Resource, CollectionResource
from stormpath.resources.custom_data import CustomData

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
    remaining_keys = set(custom_data) - set(custom_data.exposed_readonly_timestamp_attrs)
    return {k: custom_data[k] for k in remaining_keys}


class TestCustomData(SingleApplicationBase):
    """Assert CustomData behaves as expected."""

    def test_key_delete(self):
        self.app.custom_data['hi'] = 'there'
        self.app.custom_data['yo'] = 'momma'
        self.app.custom_data.save()

        app = self.client.applications.search({'name': self.app.name})[0]

        self.assertEqual(app.custom_data['hi'], 'there')
        self.assertEqual(app.custom_data['yo'], 'momma')

        del self.app.custom_data['hi']
        self.app.custom_data.save()

        app = self.client.applications.search({'name': self.app.name})[0]

        with self.assertRaises(KeyError):
            app.custom_data['hi']

        with self.assertRaises(KeyError):
            self.app.custom_data['hi']


class CustomDataTest(SingleApplicationBase):
    def setUp(self):
        super(CustomDataTest, self).setUp()
        self.custom_data_resources = {
            'applications': self.client.applications,
            'directories': self.client.directories,
        }


class TestAccountCustomData(AccountBase):

    def test_account_creation_with_custom_data(self):
        _, acc = self.create_account(self.app.accounts,
            custom_data=CUSTOM_DATA)

        acc = self.app.accounts.get(acc.href)
        self.assertEqual(CUSTOM_DATA, remove_timestamp_attrs(acc.custom_data))
        self.assertTrue(set(acc.custom_data.exposed_readonly_timestamp_attrs).issubset(set(acc.custom_data.keys())))

    def test_custom_data_behaves_as_dict(self):
        _, acc = self.create_account(self.app.accounts, custom_data=CUSTOM_DATA)
        exposed_timestamps = acc.custom_data.exposed_readonly_timestamp_attrs

        self.assertEqual(set(list(CUSTOM_DATA.keys()) + list(exposed_timestamps)), set(acc.custom_data.keys()))
        self.assertEqual(len(CUSTOM_DATA.values()) + len(exposed_timestamps), len(acc.custom_data.values()))
        self.assertEqual(len(CUSTOM_DATA.items()) + len(exposed_timestamps), len(acc.custom_data.items()))
        self.assertEqual(set(CUSTOM_DATA) | set(exposed_timestamps), set(acc.custom_data))
        self.assertEqual(acc.custom_data['foo'], CUSTOM_DATA['foo'])
        self.assertEqual(acc.custom_data.get('foo'), CUSTOM_DATA['foo'])
        self.assertEqual(acc.custom_data.get('created_at'), acc.custom_data.created_at)
        self.assertIsInstance(acc.custom_data.created_at, datetime)
        self.assertEqual(acc.custom_data.get('modified_at'), acc.custom_data.modified_at)
        self.assertIsInstance(acc.custom_data.modified_at, datetime)
        self.assertEqual(acc.custom_data.get('nonexistent', 42), 42)

    def test_custom_data_keys_work_with_dot_notation(self):
        _, acc = self.create_account(self.app.accounts)
        acc.custom_data['hi'] = 'there'
        acc.save()

        acc = self.app.accounts.query(email=acc.email)[0]
        self.assertEqual(acc.custom_data.hi, 'there')
        self.assertEqual(acc.custom_data['hi'], 'there')

        _, acc = self.create_account(self.app.accounts)
        acc.custom_data.hi = 'there'
        acc.save()

        data_field = acc.custom_data.data_field
        acc = self.app.accounts.query(email=acc.email)[0]
        self.assertEqual(id(acc.custom_data.hi), id(acc.custom_data.__dict__[data_field]['hi']))
        self.assertEqual(id(acc.custom_data['hi']), id(acc.custom_data.__dict__[data_field]['hi']))
        self.assertEqual(acc.custom_data.hi, 'there')

    def test_custom_data_modification(self):
        _, acc = self.create_account(self.app.accounts)

        self.assertEqual(set(acc.custom_data), set(acc.custom_data.exposed_readonly_timestamp_attrs))

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

        self.assertEqual(set(acc.custom_data), set(acc.custom_data.exposed_readonly_timestamp_attrs))

    def test_custom_data_set_as_dict(self):
        name, acc = self.create_account(self.app.accounts)

        self.assertEqual(set(acc.custom_data), set(acc.custom_data.exposed_readonly_timestamp_attrs))

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
            res = e.create({'name': self.get_random_name(), 'custom_data': CUSTOM_DATA})
            res = e.get(res.href)

            self.assertEqual(CUSTOM_DATA, remove_timestamp_attrs(res.custom_data))
            self.assertTrue(set(res.custom_data.exposed_readonly_timestamp_attrs).issubset(set(res.custom_data.keys())))

    def test_custom_data_behaves_as_dict(self):
        for e in self.custom_data_resources.values():
            res = e.create({'name': self.get_random_name(), 'custom_data': CUSTOM_DATA})
            exposed_timestamps = res.custom_data.exposed_readonly_timestamp_attrs

            self.assertEqual(set(list(CUSTOM_DATA.keys()) + list(exposed_timestamps)), set(res.custom_data.keys()))
            self.assertEqual(len(CUSTOM_DATA.values()) + len(exposed_timestamps), len(res.custom_data.values()))
            self.assertEqual(len(CUSTOM_DATA.items()) + len(exposed_timestamps), len(res.custom_data.items()))
            self.assertEqual(set(CUSTOM_DATA) | set(exposed_timestamps), set(res.custom_data))
            self.assertEqual(res.custom_data['foo'], CUSTOM_DATA['foo'])
            self.assertEqual(res.custom_data.get('foo'), CUSTOM_DATA['foo'])
            self.assertEqual(res.custom_data.get('nonexistent', 42), 42)
            self.assertEqual(res.custom_data.get('created_at'), res.custom_data.created_at)
            self.assertIsInstance(res.custom_data.created_at, datetime)
            self.assertEqual(res.custom_data.get('modified_at'), res.custom_data.modified_at)
            self.assertIsInstance(res.custom_data.modified_at, datetime)

    def test_custom_data_modification(self):
        for e in self.custom_data_resources.values():
            res = e.create({'name': self.get_random_name()})

            self.assertEqual(set(res.custom_data), set(res.custom_data.exposed_readonly_timestamp_attrs))

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

            self.assertEqual(set(res.custom_data), set(res.custom_data.exposed_readonly_timestamp_attrs))


class TestGroupCustomData(SingleApplicationBase):

    def test_creation_with_custom_data(self):
        res = self.app.groups.create({'name': self.get_random_name(), 'custom_data': CUSTOM_DATA})
        res = self.app.groups.get(res.href)

        self.assertEqual(CUSTOM_DATA, remove_timestamp_attrs(res.custom_data))
        self.assertTrue(set(res.custom_data.exposed_readonly_timestamp_attrs).issubset(set(res.custom_data.keys())))

    def test_custom_data_behaves_as_dict(self):
        res = self.app.groups.create({'name': self.get_random_name(), 'custom_data': CUSTOM_DATA})
        exposed_timestamps = res.custom_data.exposed_readonly_timestamp_attrs

        self.assertEqual(set(list(CUSTOM_DATA.keys()) + list(exposed_timestamps)), set(res.custom_data.keys()))
        self.assertEqual(len(CUSTOM_DATA.values()) + len(exposed_timestamps), len(res.custom_data.values()))
        self.assertEqual(len(CUSTOM_DATA.items()) + len(exposed_timestamps), len(res.custom_data.items()))
        self.assertEqual(set(CUSTOM_DATA) | set(exposed_timestamps), set(res.custom_data))
        self.assertEqual(res.custom_data['foo'], CUSTOM_DATA['foo'])
        self.assertEqual(res.custom_data.get('foo'), CUSTOM_DATA['foo'])
        self.assertEqual(res.custom_data.get('nonexistent', 42), 42)
        self.assertEqual(res.custom_data.get('created_at'), res.custom_data.created_at)
        self.assertIsInstance(res.custom_data.created_at, datetime)
        self.assertEqual(res.custom_data.get('modified_at'), res.custom_data.modified_at)
        self.assertIsInstance(res.custom_data.modified_at, datetime)

    def test_custom_data_modification(self):
        res = self.app.groups.create({'name': self.get_random_name()})

        self.assertEqual(set(res.custom_data), set(res.custom_data.exposed_readonly_timestamp_attrs))

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

        self.assertEqual(set(res.custom_data), set(res.custom_data.exposed_readonly_timestamp_attrs))

    def test_custom_data_search(self):
        self.dir.groups.create({'name': self.get_random_name() + 'group1', 'custom_data': CUSTOM_DATA})
        self.dir.groups.create({'name': self.get_random_name() + 'group2', 'custom_data': {'omg': 'noway'}})
        self.dir.groups.create({'name': self.get_random_name() + 'group3', 'custom_data': {'omg': ['wow', 'cool']}})

        for group in self.dir.groups.search('customData.omg=noway'):
            self.assertTrue('group2' in group.name)
            self.assertEqual(group.custom_data['omg'], 'noway')

        for gorup in self.dir.groups.earch('customData.omg=wow'):
            self.assertTrue('group3' in group.name)
            self.assertTrue(group.custom_data['omg'], ['wow', 'cool'])


class TestTenantCustomData(SingleApplicationBase):

    def setUp(self):
        super(TestTenantCustomData, self).setUp()
        self.client.tenant.custom_data.delete()
        self.exposed_timestamps = self.client.tenant.custom_data.exposed_readonly_timestamp_attrs

    def tearDown(self):
        super(TestTenantCustomData, self).tearDown()
        self.client.tenant.custom_data.delete()

    def test_tenant_has_custom_data_with_exposed_timestamp_attrs(self):
        self.assertEqual(set(self.client.tenant.custom_data), set(self.exposed_timestamps))

    def test_tenant_with_custom_data(self):
        self.client.tenant.custom_data['testCamelCase'] = 'TEST'
        self.client.tenant.save()

        self.assertEqual({'testCamelCase': 'TEST'}, remove_timestamp_attrs(self.client.tenant.custom_data))
        self.assertTrue(set(self.client.tenant.custom_data.exposed_readonly_timestamp_attrs).issubset(set(self.client.tenant.custom_data.keys())))

    def test_custom_data_behaves_as_dict(self):
        res = self.client.tenant
        exposed_timestamps = res.custom_data.exposed_readonly_timestamp_attrs

        for key in CUSTOM_DATA.keys():
            res.custom_data[key] = CUSTOM_DATA[key]

        self.assertEqual(set(list(CUSTOM_DATA.keys()) + list(exposed_timestamps)), set(res.custom_data.keys()))
        self.assertEqual(len(CUSTOM_DATA.values()) + len(exposed_timestamps), len(res.custom_data.values()))
        self.assertEqual(len(CUSTOM_DATA.items()) + len(exposed_timestamps), len(res.custom_data.items()))
        self.assertEqual(set(CUSTOM_DATA) | set(self.exposed_timestamps), set(res.custom_data))
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

    def test_groups_custom_data_search(self):
        tenant = self.client.tenant

        self.dir.groups.create({'name': self.get_random_name() + 'group1', 'custom_data': CUSTOM_DATA})
        self.dir.groups.create({'name': self.get_random_name() + 'group2', 'custom_data': {'omg': 'noway'}})

        for group in tenant.groups.search('customData.omg=noway'):
            self.assertTrue('group2' in group.name)
            self.assertEqual(group.custom_data['omg'], 'noway')


class TestCustomDataMock(TestCase):
    def setUp(self):
        self.created_at = datetime(2014, 7, 16, 13, 48, 22, 378000, tzinfo=tzutc())
        self.modified_at = datetime(2014, 7, 16, 13, 48, 22, 378000, tzinfo=tzoffset(None, -1 * 60 * 60))
        self.props = {
            'href': 'test/resource',
            'sp_http_status': 200,
            'createdAt': '2014-07-16T13:48:22.378Z',
            'modifiedAt': '2014-07-16T13:48:22.378-01:00',
            'foo': 1,
            'bar': '2',
            'baz': ['one', 'two', 'three'],
            'quux': {'key': 'value'}
        }

    def test_custom_data_created_with_properties(self):
        d = CustomData(MagicMock(), properties=self.props)

        self.assertEqual(d['foo'], 1)

    def test_readonly_properties_are_not_exposed_in_dict(self):
        d = CustomData(MagicMock(), properties=self.props)

        self.assertEqual(d.href, 'test/resource')
        self.assertFalse('href' in d)

    def test_readonly_properties_are_not_camels(self):
        d = CustomData(MagicMock(), properties=self.props)

        with self.assertRaises(AttributeError):
            self.createdAt

        self.assertEqual(d.created_at, self.created_at)

    def test_exposed_readonly_timestamp_values_in_dict_are_datetime(self):
        d = CustomData(MagicMock(), properties=self.props)

        self.assertIsInstance(d['created_at'], datetime)
        self.assertIsInstance(d['modified_at'], datetime)

    def test_custom_data_implements_dict_protocol(self):
        d = CustomData(MagicMock(), properties=self.props)

        self.assertTrue('created_at' in d)
        self.assertTrue('modified_at' in d)
        self.assertTrue('foo' in d)
        self.assertEqual(d['foo'], 1)
        self.assertEqual(d['created_at'], self.created_at)
        self.assertEqual(d['modified_at'], self.modified_at)
        self.assertEqual(d.get('foo'), 1)
        self.assertEqual(d.get('created_at'), self.created_at)
        self.assertEqual(d.get('modified_at'), self.modified_at)
        self.assertEqual(d.get('nonexistent'), None)
        self.assertEqual(d.get('nonexistent', 42), 42)

        with self.assertRaises(KeyError):
            d['nonexistent']

        keys = set(sorted(d.keys(), key=str))
        self.assertEqual(keys, set(d))
        self.assertEqual(keys, {'created_at', 'modified_at', 'bar', 'baz', 'foo', 'quux'})
        values = sorted(list(d.values()), key=str)

        keys_from_items = {k for k, v in d.items()}
        values_from_items = sorted([v for k, v in d.items()], key=str)

        self.assertEqual(keys, keys_from_items)
        self.assertEqual(values, values_from_items)

    def test_non_readonly_properties_can_be_set(self):
        d = CustomData(MagicMock(), properties=self.props)

        d['whatever'] = 42
        self.assertEqual(d['whatever'], 42)

    def test_readonly_properties_cant_be_set(self):
        d = CustomData(MagicMock(), properties=self.props)

        with self.assertRaises(KeyError):
            d['meta'] = 'i-am-so-meta'

    def test_exposed_readonly_properties_cant_be_set(self):
        d = CustomData(MagicMock(), properties=self.props)

        with self.assertRaises(KeyError):
            d['created_at'] = 111

        with self.assertRaises(KeyError):
            d['createdAt'] = 111

    def test_exposed_readonly_properties_cant_be_deleted(self):
        d = CustomData(MagicMock(), properties=self.props)

        with self.assertRaises(KeyError):
            del d['created_at']

    def test_camelcase_readonly_properties_cant_be_set(self):
        d = CustomData(MagicMock(), properties=self.props)

        with self.assertRaises(KeyError):
            d['sp_meta'] = 'i-am-so-sp-meta'

        with self.assertRaises(KeyError):
            d['spMeta'] = 'i-am-so-sp-meta'

    def test_del_properties_doesnt_trigger_resource_delete(self):
        ds = MagicMock()
        client = MagicMock(data_store=ds)

        d = CustomData(client, properties=self.props)

        del d['foo']
        self.assertFalse('foo' in d)

        self.assertFalse(ds.delete_resource.called)

    def test_serializing_props_only_serializes_custom_data(self):
        d = CustomData(MagicMock(), properties=self.props)

        del self.props['href']
        del self.props['createdAt']
        del self.props['sp_http_status']

        props = {k: self.props[k] for k in set(self.props) - {'modifiedAt'}}
        self.assertEqual(d._get_properties(), props)

    def test_manually_set_property_has_precedence(self):
        props = {
            'href': 'test/resource',
            'bar': '2',
            'baz': ['one', 'two', 'three'],
            'quux': {'key': 'value'}
        }

        d = CustomData(MagicMock(), properties=props)

        d['quux'] = 'a-little-corgi'
        d._set_properties(props)

        quux = d._data.pop('quux')
        props.pop('quux')
        props.pop('href')

        # quux property is as set
        self.assertEqual(quux, 'a-little-corgi')
        self.assertEqual(d._data, props)

    def test_del_delays_deletion_until_save(self):
        ds = MagicMock()
        client = MagicMock(data_store=ds)

        d = CustomData(client, properties=self.props)
        del d['foo']
        del d['bar']

        self.assertFalse(ds.delete_resource.called)

        d.save()

        ds.delete_resource.assert_any_call('test/resource/foo')
        ds.delete_resource.assert_any_call('test/resource/bar')
        self.assertEqual(ds.delete_resource.call_count, 2)

    @patch('stormpath.resources.base.Resource.is_new')
    def test_del_doesnt_delete_if_new_resource(self, is_new):
        is_new.return_value = True
        ds = MagicMock()
        client = MagicMock(data_store=ds)

        d = CustomData(client, properties=self.props)
        del d['foo']
        is_new.return_value = False
        d.save()

        self.assertFalse(ds.delete_resource.called)

    def test_save_empties_delete_list(self):
        ds = MagicMock()
        client = MagicMock(data_store=ds)

        d = CustomData(client, properties=self.props)
        del d['foo']
        d.save()
        ds.delete_resource.reset_mock()
        d.save()

        self.assertFalse(ds.delete_resource.called)

    def test_setitem_removes_from_delete_list(self):
        ds = MagicMock()
        client = MagicMock(data_store=ds)

        d = CustomData(client, properties=self.props)
        del d['foo']
        d['foo'] = 'i-wasnt-even-gone'

        self.assertFalse(ds.delete_resource.called)

    def test_del_then_read_doesnt_set_deleted(self):
        props = {
            'href': 'test/resource',
            'bar': '2',
            'baz': ['one', 'two', 'three'],
            'quux': {'key': 'value'}
        }
        ds = MagicMock()
        ds.get_resource.return_value = self.props
        client = MagicMock(data_store=ds)

        d = CustomData(client, properties=props)
        del d['foo']

        with self.assertRaises(KeyError):
            d['foo']

        d.save()
        ds.delete_resource.assert_called_once_with('test/resource/foo')

    def test_doesnt_schedule_del_if_new_property(self):
        ds = MagicMock()
        ds.get_resource.return_value = self.props
        client = MagicMock(data_store=ds)
        d = CustomData(client, properties=self.props)

        with self.assertRaises(KeyError):
            del d['corge']

        d.save()

        self.assertFalse(ds.delete_resource.called)

    def test_dash_not_allowed_at_beggining_of_key(self):
        ds = MagicMock()
        client = MagicMock(data_store=ds)
        d = CustomData(client, properties=self.props)

        with self.assertRaises(KeyError):
            d['-'] = 'dashing'

    def test_saving_does_not_mangle_property_names(self):
        props = {
            'href': 'test/resource',
            'foo_with_underscores': 1,
            'camelCaseBar': 2,
            'baz': {
                'baz_value': True,
                'bazCamelCase': False,
                'quux': [
                    'one',
                    'two',
                    {'value_three': 3, 'valueThreeCamel': 3}
                ]
            }
        }
        ds = MagicMock()
        client = MagicMock(data_store=ds)

        d = CustomData(client, properties=props)
        d['another_underscores'] = 3
        d['anotherCamelCase'] = 4
        d.save()

        ds.update_resource.assert_called_once_with('test/resource', {
            'foo_with_underscores': 1,
            'camelCaseBar': 2,
            'another_underscores': 3,
            'anotherCamelCase': 4,
            'baz': {
                'baz_value': True,
                'bazCamelCase': False,
                'quux': [
                    'one',
                    'two',
                    {'value_three': 3, 'valueThreeCamel': 3}
                ]
            }
        })

    def test_creation_with_custom_data_does_not_mangle_cd_keys(self):
        ds = MagicMock()

        class Res(Resource):
            writable_attrs = ('sub_resource',)

            @staticmethod
            def get_resource_attributes():
                return {'sub_resource': CustomData}

        class ResList(CollectionResource):
            resource_class = Res

        rl = ResList(
            client = MagicMock(data_store=ds, BASE_URL='http://www.example.com'),
            properties={'href': '/'},
        )
        cd = {
            'foo_value': 42,
            'bar_dict': {
                'bar_value': True,
                'barCamelCase': False
            }
        }

        rl.create({'sub_resource': cd})
        ds.create_resource.assert_called_once_with('http://www.example.com/', {'subResource': cd}, params={})

    def test_cusom_data_elem_in_dict_check(self):
        from stormpath.resources.account import Account

        ds = MagicMock()
        ds.get_resource.return_value = {'href': 'test/customData', 'test': 1}

        client = MagicMock(data_store=ds)
        client.accounts.get.return_value = Account(client, properties={
            'href': 'test/account',
            'custom_data': {'href': 'test/customData'}
        })
        a = client.accounts.get('test/account')

        self.assertTrue('test' in a.custom_data)

    def test_custom_data_deletion(self):
        ds = MagicMock()
        client = MagicMock(data_store=ds)

        d = CustomData(client, properties=self.props)
        d.delete()

        ds.delete_resource.assert_called_once_with(self.props['href'])
        assert {} == dict(d)

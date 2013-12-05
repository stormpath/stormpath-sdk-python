from unittest import TestCase, main
try:
    from mock import MagicMock, patch
except ImportError:
    from unittest.mock import MagicMock, patch

from stormpath.resource.custom_data import CustomData


class TestCustomData(TestCase):

    def setUp(self):
        self.props = {
            'href': 'test/resource',
            'created_at': 123,
            'foo': 1,
            'bar': '2',
            'baz': ['one', 'two', 'three'],
            'quux': {'key': 'value'}
        }

    def test_custom_data_created_with_properties(self):
        d = CustomData(MagicMock(), properties=self.props)

        self.assertTrue(d.is_materialized())
        self.assertEqual(d['foo'], 1)

    def test_readonly_properties_are_not_exposed_in_dict(self):
        d = CustomData(MagicMock(), properties=self.props)

        self.assertEqual(d.href, 'test/resource')
        self.assertFalse('href' in d)

    def test_custom_data_implements_dict_protocol(self):
        d = CustomData(MagicMock(), properties=self.props)

        self.assertTrue('foo' in d)
        self.assertEqual(d['foo'], 1)
        self.assertEqual(d.get('foo'), 1)
        self.assertEqual(d.get('nonexistent'), None)
        self.assertEqual(d.get('nonexistent', 42), 42)

        with self.assertRaises(KeyError):
            d['nonexistent']

        keys = set(sorted(d.keys(), key=str))
        self.assertEqual(keys, set(d))
        self.assertEqual(keys, {'bar', 'baz', 'foo', 'quux'})
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

    def test_deleting_properties_triggers_resource_delete(self):
        ds = MagicMock()
        client = MagicMock(data_store=ds)

        d = CustomData(client, properties=self.props)

        del d['foo']
        self.assertFalse('foo' in d)

        ds.delete_resource.assert_called_once_with('test/resource/foo')

    def test_serializing_props_only_serializes_custom_data(self):
        d = CustomData(MagicMock(), properties=self.props)

        del self.props['href']
        del self.props['created_at']

        self.assertEqual(d._get_properties(), self.props)

    def test_manually_set_property_has_precedence(self):
        props = {
            'bar': '2',
            'baz': ['one', 'two', 'three'],
            'quux': {'key': 'value'}
        }

        d = CustomData(MagicMock(), properties=props)

        d['quux'] = 'a-little-corgi'
        d._set_properties(props)

        quux = d.data.pop('quux')
        props.pop('quux')

        # quux property is as set
        self.assertEqual(quux, 'a-little-corgi')
        self.assertEqual(d.data, props)

    @patch('stormpath.resource.base.Resource._ensure_data')
    def test_non_materialized_property_is_ensured(self, _ensure_data):
        d = CustomData(MagicMock(), properties=self.props)
        d.get('corge')

        self.assertTrue(_ensure_data.called)

if __name__ == '__main__':
    main()

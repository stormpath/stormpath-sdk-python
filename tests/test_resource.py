from unittest import TestCase, main

from mock import MagicMock
from stormpath.resource.base import Expansion, Resource, ResourceList


class TestExpansion(TestCase):

    def test_expansion(self):

        e = Expansion('foo', 'bar', 'baz')
        e.add_property('bar', limit=5)

        p = sorted(e.get_params().split(','))

        self.assertEqual(p, ['bar(limit:5)', 'baz', 'foo'])

    def test_expansion_limit_offset(self):
        e = Expansion()
        e.add_property('quux', limit=5, offset=10)

        p = e.get_params()

        self.assertTrue(p == 'quux(limit:5,offset:10)' or
            p == 'quux(offset:10,limit:5)')


class TestCamelCaseConversions(TestCase):

    def test_to_camel_case(self):

        to_cc = Resource.to_camel_case

        self.assertEqual(to_cc(''), '')
        self.assertEqual(to_cc('foo'), 'foo')
        self.assertEqual(to_cc('foo_bar'), 'fooBar')
        self.assertEqual(to_cc('foo_bar_baz'), 'fooBarBaz')

    def test_from_camel_case(self):

        from_cc = Resource.from_camel_case

        self.assertEqual(from_cc(''), '')
        self.assertEqual(from_cc('foo'), 'foo')
        self.assertEqual(from_cc('fooBar'), 'foo_bar')
        self.assertEqual(from_cc('fooBarBaz'), 'foo_bar_baz')
        self.assertEqual(from_cc('foo123Bar'), 'foo123_bar')


class TestBaseResource(TestCase):

    def test_resource_init_by_href(self):
        r = Resource(MagicMock(), href='test/resource')

        # it's not materialized yet
        self.assertFalse(r.is_materialized())
        # it's not new (has href)
        self.assertFalse(r.is_new())
        # it know what it is
        self.assertEqual(r.href, 'test/resource')
        # href is not writable
        with self.assertRaises(AttributeError):
            r.href = 'abc'
        # non-existing attribute access is handled correctly
        with self.assertRaises(AttributeError):
            r.foo

    def test_resource_init_by_properties(self):
        r = Resource(MagicMock(), properties={
            'href': 'test/resource',
            'name': 'Test Resource',
            'someProperty': 'value'
        })

        # we have the resource data
        self.assertTrue(r.is_materialized())
        # it's not new (has href)
        self.assertFalse(r.is_new())
        # it knows what it is
        self.assertEqual(r.href, 'test/resource')
        # we can access the attributes
        self.assertEqual(r.name, 'Test Resource')
        # attribute name was correctly converted
        self.assertEqual(r.some_property, 'value')
        # there are no writable attributes
        with self.assertRaises(AttributeError):
            r.name = 5

    def test_resource_materialization(self):
        ds = MagicMock()
        ds.get_resource.return_value = {
            'href': 'test/resource',
            'name': 'Test Resource'
        }

        r = Resource(MagicMock(data_store=ds), href='test/resource')
        name = r.name

        ds.get_resource.assert_called_once_with('test/resource', params=None)
        self.assertEqual(name, 'Test Resource')


    def test_readwrite_attributes(self):

        class Res(Resource):
            readwrite_attrs = ('name')

        r = Res(MagicMock(), properties={
            'href': 'test/resource',
            'name': 'Test Resource',
        })

        r.name = 'foo'
        self.assertEqual(r.name, 'foo')

    def test_resource_attributes(self):

        class Res(Resource):
            def get_resource_attributes(self):
                return {'related': Resource}

        r = Res(MagicMock(), properties={
            'href': 'test/resource',
            'name': 'Test Resource',
            'related': {'href': 'another/resource'}
        })

        r2 = r.related

        self.assertTrue(isinstance(r2, Resource))
        self.assertEqual(r2.href, 'another/resource')

    def test_resource_expansion(self):

        class Res(Resource):
            def get_resource_attributes(self):
                return {'related': Resource}

        ds = MagicMock()
        ds.get_resource.return_value = {
            'href': 'test/resource',
            'name': 'Test Resource',
            'related': {
                'href': 'related/resource',
                'name': 'Related Resource'
            }
        }

        r = Res(MagicMock(data_store=ds), href='test/resource',
            expand=Expansion('related'))

        name = r.name

        ds.get_resource.assert_called_once_with('test/resource',
            params={'expand': 'related'})

        self.assertEqual(name, 'Test Resource')
        self.assertEqual(r.related.name, 'Related Resource')

    def test_deletion(self):
        ds = MagicMock()
        ds.delete_resource.return_value.status_code = 204

        r = Resource(MagicMock(data_store=ds), href='test/resource')
        r.delete()

        ds.delete_resource.assert_called_once_with('test/resource')

    def test_update(self):
        ds = MagicMock()
        ds.update_resource.return_value.status_code = 200

        class Res(Resource):
            readwrite_attrs = ('some_property')

        r = Res(MagicMock(data_store=ds), href='test/resource')
        r.some_property = 'hello world'
        r.save()

        ds.update_resource.assert_called_once_with('test/resource', {
            'someProperty': 'hello world'
        })


class TestResourceList(TestCase):

    def test_init_by_properties(self):
        rl = ResourceList(client=MagicMock(), properties={
            'href': '/',
            'offset': 0,
            'limit': 25,
            'items': [
                {'href': 'test/resource'},
                {'href': 'another/resource'}
            ]
        })

        self.assertTrue(rl.is_materialized())

        # test length computation
        self.assertEqual(len(rl), 2)
        # test indexing
        self.assertEqual(rl[0].href, 'test/resource')
        self.assertEqual(rl[1].href, 'another/resource')
        # test iteration
        hrefs = [r.href for r in rl]
        self.assertTrue(hrefs, ['test/resource', 'another/resource'])

    def test_limit_offset_query(self):
        ds = MagicMock()
        ds.get_resource.return_value = {
            'offset': 5,
            'limit': 5,
            'items': []
        }

        rl = ResourceList(client=MagicMock(data_store=ds), href='/')

        rl2 = rl.query(offset=5, limit=5)
        self.assertEqual(ds.get_resource.call_count, 0)

        list(rl2)
        ds.get_resource.assert_called_once_with('/', params={
            'offset': 5,
            'limit': 5})

        self.assertEqual(rl2.offset, 5)
        self.assertEqual(rl2.limit, 5)

    def test_query_by_slicing(self):
        ds = MagicMock()
        ds.get_resource.return_value = {
            'offset': 2,
            'limit': 8,
            'items': []
        }

        rl = ResourceList(client=MagicMock(data_store=ds), href='/')

        rl2 = rl[2:10]
        self.assertEqual(ds.get_resource.call_count, 0)

        list(rl2)
        ds.get_resource.assert_called_once_with('/', params={
            'offset': 2,
            'limit': 8})

        self.assertEqual(rl2.offset, 2)
        self.assertEqual(rl2.limit, 8)

    def test_pagination(self):
        ds = MagicMock()
        ds.get_resource.return_value = {
            'href': '/',
            'offset': 2,
            'limit': 2,
            'items': [
                {'href': 'third/resource'}
            ]
        }

        rl = ResourceList(client=MagicMock(data_store=ds), properties={
            'href': '/',
            'offset': 0,
            'limit': 2,
            'items': [
                {'href': 'test/resource'},
                {'href': 'another/resource'}
            ]
        })

        hrefs = [r.href for r in rl]

        self.assertEqual(hrefs, ['test/resource', 'another/resource',
            'third/resource'])

        ds.get_resource.assert_called_once_with('/', params={
            'offset': 2,
            'limit': 2
        })

        self.assertEqual(len(rl), 3)
        self.assertEqual(rl.offset, 0)
        self.assertEqual(rl.limit, 3)

        # check that repeated iteration doesn't try to continue pagination
        list(rl)
        self.assertEqual(ds.get_resource.call_count, 1)

    def test_creation_with_workflow_param_passing(self):
        ds = MagicMock()
        ds.create_resource.return_value = {
            'href': 'test/resource',
            'name': 'Test Resource',
        }

        rl = ResourceList(
            client=MagicMock(data_store=ds,
                BASE_URL='http://www.example.com'),
            properties={
                'href': '/',
            })

        r = rl.create({}, some_param=True)

        ds.create_resource.assert_called_once_with('http://www.example.com/',
            {}, params={'someParam': True})

        self.assertTrue(r.href, 'test/resource')
        self.assertTrue(r.name, 'Test Resource')

    def test_get_single_app_by_indexing_and_get(self):
        rl = ResourceList(client=MagicMock(), properties={
            'href': '/',
            'offset': 0,
            'limit': 25,
            'items': [
                {'href': 'test/resource'},
                {'href': 'another/resource'}
            ]
        })

        a = rl[0]
        b = rl['test/resource']
        c = rl.get('another/resource')

        self.assertEqual(a.href, 'test/resource')
        self.assertEqual(b.href, 'test/resource')
        self.assertEqual(c.href, 'another/resource')

if __name__ == '__main__':
    main()

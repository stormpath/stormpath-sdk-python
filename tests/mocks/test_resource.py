from unittest import TestCase, main
from datetime import datetime
from dateutil.tz import tzutc, tzoffset
from stormpath.resources.agent import AgentConfig

try:
    from mock import MagicMock, patch, create_autospec
except ImportError:
    from unittest.mock import MagicMock, patch, create_autospec
from stormpath.resources.base import (Expansion, Resource, CollectionResource,
    SaveMixin, DeleteMixin, AutoSaveMixin, DictMixin, FixedAttrsDict)
from stormpath.client import Client

from stormpath.resources.application import Application
from stormpath.resources import Provider


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

    def test_resource_with_href_not_string_type(self):
        self.assertRaises(TypeError, Resource, MagicMock(), href=123)

    def test_resource_without_neither_href_not_properties(self):
        self.assertRaises(ValueError, Resource, MagicMock())

    def test_getting_resource_property_names(self):
        r = Resource(
                MagicMock(),
                properties={'href': 'reshref', '_some_property': 'should not show up'})
        self.assertEqual(['href'], r._get_property_names())

    def test_resource_dir_method(self):
        r = Resource(
                MagicMock(),
                properties={'href': 'reshref', '_some_property': 'should not show up'})
        r._ensure_data = lambda : None

        self.assertEqual(['href'], r.__dir__())

    def test_resource_repr_method(self):
        r = Resource(
                MagicMock(),
                properties={'href': 'reshref'})
        self.assertEqual('<Resource href=reshref>', r.__repr__())

    def test_resource_str_method(self):
        r = Resource(
                MagicMock(),
                properties={'href': 'reshref'})
        self.assertEqual('<Resource href=reshref>', r.__str__())
        r = Resource(
                MagicMock(),
                properties={'name': 'name'})
        self.assertEqual('name', r.__str__())

    def test_save_wont_save_new_resources(self):
        r = Application(
                MagicMock(),
                properties={})
        self.assertRaises(ValueError, r.save)

    def test_deleting_new_resource(self):
        r = Application(
                MagicMock(),
                properties={})
        self.assertIsNone(r.delete())

    def test_resource_status_is_disabled_if_not_specified(self):
        r = Application(
                MagicMock(),
                properties={})
        self.assertEqual(r.STATUS_DISABLED, r.get_status())

    def test_getting_resource_status(self):
        r = Application(
                MagicMock(),
                properties={'status': Application.STATUS_ENABLED})
        self.assertEqual(r.STATUS_ENABLED, r.get_status())

    def test_checking_if_status_enabled(self):
        r = Application(
                MagicMock(),
                properties={'status': Application.STATUS_ENABLED})
        self.assertTrue(r.is_enabled())

    def test_checking_if_status_disabled(self):
        r = Application(
                MagicMock(),
                properties={})
        self.assertTrue(r.is_disabled())

    def test_sanitize_property(self):
        ret = Resource._sanitize_property({'full_name': 'full name'})
        self.assertEqual({'fullName': 'full name'}, ret)

    def test_wrapping_resource_attrs(self):
        r = Resource(MagicMock(), properties={})
        to_wrap = Resource(MagicMock(), properties={})
        ret = r._wrap_resource_attr(Application, to_wrap)
        self.assertEqual(to_wrap, ret)

        ret = r._wrap_resource_attr(Application, {'name': 'some app'})
        self.assertEqual('some app', ret.name)
        self.assertTrue(isinstance(ret, Application))

        ret = r._wrap_resource_attr(Application, None)
        self.assertIsNone(ret)

        self.assertRaises(TypeError, r._wrap_resource_attr, Application, 'Unsupported Conversion')

    def test_getting_items_from_dict_mixing(self):
        r = Application(MagicMock(), properties={'name': 'some app'})
        self.assertEqual([('name', 'some app')], r.items())

    def test_iter_method_on_dict_mixin(self):
        r = Application(MagicMock(), properties={'name': 'some app'})
        self.assertEqual(['name'], list(r.__iter__()))

    def test_search_method_on_collection(self):
        c = CollectionResource(MagicMock(), properties={'href': 'href'})
        ret = c.search({'q': 'some_query'})
        self.assertEqual({'q': 'some_query'}, ret._query)

        ret = c.search('some_query')
        self.assertEqual({'q': 'some_query'}, ret._query)

    def test_resource_init_by_properties(self):
        r = Resource(MagicMock(), properties={
            'href': 'test/resource',
            'createdAt': '2014-07-16T13:48:22.378Z',
            'modifiedAt': '2014-07-16T13:48:22.378+01:00',
            'name': 'Test Resource',
            'someProperty': 'value'
        })

        # it's not new (has href)
        self.assertFalse(r.is_new())
        # it knows what it is
        self.assertEqual(r.href, 'test/resource')
        # we can access the attributes
        self.assertEqual(r.name, 'Test Resource')
        # there is created_at attribute
        self.assertEqual(
            r.created_at,
            datetime(2014, 7, 16, 13, 48, 22, 378000, tzinfo=tzutc()))
        # there is modified_at attribute
        self.assertEqual(
            r.modified_at,
            datetime(
                2014, 7, 16, 13, 48, 22, 378000, tzinfo=tzoffset(None, 3600)))
        # attribute name was correctly converted
        self.assertEqual(r.some_property, 'value')
        # there are no writable attributes
        with self.assertRaises(AttributeError):
            r.name = 5
        with self.assertRaises(AttributeError):
            r.created_at = 'whatever'
        with self.assertRaises(AttributeError):
            r.modified_at = 'whatever'

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

    def test_writable_attributes(self):

        class Res(Resource):
            writable_attrs = ('name',)

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

        class Res(Resource, DeleteMixin):
            pass

        r = Res(MagicMock(data_store=ds), href='test/resource')
        r.delete()

        ds.delete_resource.assert_called_once_with('test/resource')

    def test_update(self):
        ds = MagicMock()
        ds.update_resource.return_value.status_code = 200

        class Res(Resource, SaveMixin):
            writable_attrs = ('some_property',)

        r = Res(MagicMock(data_store=ds), href='test/resource')
        r.some_property = 'hello world'
        r.save()

        ds.update_resource.assert_called_once_with('test/resource', {
            'someProperty': 'hello world'
        })

    def test_autosave(self):
        ds = MagicMock()
        autosave_ds = MagicMock()
        class Res(Resource, AutoSaveMixin):
            writable_attrs = ('some_property', 'special_resource')
            autosaves = ('special_resource',)

        class SubRes(Resource, SaveMixin):
            pass

        r = Res(MagicMock(data_store=ds), properties={
            "href": "test/resource",
            "specialResource": {"href": "test/resource"}})
        r.special_resource = SubRes(MagicMock(data_store=autosave_ds),
            href='test/autosave_resource')

        r.some_property = 'hello world'
        r.save()

        self.assertTrue(ds.update_resource.called)
        self.assertTrue(autosave_ds.update_resource.called)

    def test_autosave_checks_list_of_allowed_saves(self):
        ds = MagicMock()
        autosave_ds = MagicMock()

        class Res(Resource, AutoSaveMixin):
            writable_attrs = ('some_property', 'special_resource')
            autosaves = ()

        r = Res(MagicMock(data_store=ds), properties={
            "href": "test/resource",
            "specialResource": {"href": "test/resource"}})
        r.special_resource = Res(MagicMock(data_store=autosave_ds),
            href='test/autosave_resource')

        r.some_property = 'hello world'
        r.save()

        self.assertTrue(ds.update_resource.called)
        self.assertFalse(autosave_ds.update_resource.called)

    def test_dict_mixin(self):

        class Res(Resource, DictMixin):
            writable_attrs = ('foo_val', 'bar')

        props_raw = {
            'href': 'test/resource',
            'fooVal': 'FOO',
            'baz': 'BAZ'
        }
        props = {
            'href': 'test/resource',
            'foo_val': 'FOO',
            'baz': 'BAZ'
        }

        r = Res(MagicMock(), properties=props_raw)
        self.assertEqual(dict(r), props)

        self.assertTrue('foo_val' in r)
        self.assertEqual(set(r.keys()), set(props.keys()))
        self.assertEqual(set(r.values()), set(props.values()))

        r['foo_val'] = 42
        self.assertEqual(r.foo_val, 42)

        with self.assertRaises(AttributeError):
            r['baz'] = 1

    def test_dict_mixin_update_does_update_on_server(self):
        ds = MagicMock()

        class Res(Resource, SaveMixin, DictMixin):
            writable_attrs = ('foo_val', 'bar')

        r = Res(MagicMock(data_store=ds), href='test/resource')

        r.update({
            'foo_val': True,
            'bar': False
        })

        ds.update_resource.assert_called_once_with('test/resource',
            {'fooVal': True, 'bar': False})


class TestCollectionResource(TestCase):

    def test_init_by_properties(self):
        ds = MagicMock()
        ds.get_resource.return_value = {
            'href': '/',
            'offset': 0,
            'limit': 25,
            'size': 2,
            'items': [
                {'href': 'test/resource'},
                {'href': 'another/resource'}
            ]
        }

        rl = CollectionResource(client=MagicMock(data_store=ds), properties={
            'href': '/',
            'offset': 0,
            'limit': 25,
            'size': 2,
            'items': [
                {'href': 'test/resource'},
                {'href': 'another/resource'}
            ]
        })

        # test length computation
        self.assertEqual(len(rl), 2)
        # test indexing
        self.assertEqual(rl[0].href, 'test/resource')
        self.assertEqual(rl[1].href, 'another/resource')
        # test iteration
        hrefs = [r.href for r in rl]
        self.assertTrue(hrefs, ['test/resource', 'another/resource'])

    def test_len(self):
        ds = MagicMock()
        ds.get_resource.return_value = {
            'href': '/',
            'offset': 0,
            'limit': 25,
            'size': 2,
            'items': [
                {'href': 'test/resource'},
                {'href': 'another/resource'}
            ]
        }

        rl = CollectionResource(client=MagicMock(data_store=ds), href='/')

        len_rl = len(rl)
        # assert that it will get resource from data store
        self.assertEqual(ds.get_resource.call_count, 1)
        # assert that it will get the right len
        self.assertEqual(len_rl, 2)

        ds.get_resource.return_value = {
            'href': '/',
            'offset': 0,
            'limit': 25,
            'size': 3,
            'items': [
                {'href': 'test/resource'},
                {'href': 'another/resource'},
                {'href': 'third/resource'}
            ]
        }

        len_rl = len(rl)
        # assert that it will get resource from data store again
        self.assertEqual(ds.get_resource.call_count, 2)
        # assert that it will get the new len
        self.assertEqual(len_rl, 3)

    def test_iter(self):
        ds = MagicMock()
        ds.get_resource.return_value = {
            'href': '/',
            'offset': 0,
            'limit': 25,
            'size': 2,
            'items': [
                {'href': 'test/resource'},
                {'href': 'another/resource'}
            ]
        }

        rl = CollectionResource(client=MagicMock(data_store=ds), href='/')

        hrefs = []
        for r in rl:
            hrefs.append(r.href)
        # assert that it will get resource from data store
        self.assertEqual(ds.get_resource.call_count, 1)
        # assert that it will get the right hrefs
        self.assertEqual(hrefs, ['test/resource', 'another/resource'])

        ds.get_resource.return_value = {
            'href': '/',
            'offset': 0,
            'limit': 25,
            'size': 3,
            'items': [
                {'href': 'test/resource'},
                {'href': 'another/resource'},
                {'href': 'third/resource'}
            ]
        }

        hrefs = []
        for r in rl:
            hrefs.append(r.href)
        # assert that it will get resource from data store again
        self.assertEqual(ds.get_resource.call_count, 2)
        # assert that it will get the new hrefs
        self.assertEqual(
            hrefs, ['test/resource', 'another/resource', 'third/resource'])

    def test_limit_offset_query(self):
        ds = MagicMock()
        ds.get_resource.return_value = {
            'offset': 5,
            'limit': 5,
            'size': 0,
            'items': []
        }

        rl = CollectionResource(client=MagicMock(data_store=ds), href='/')

        rl2 = rl.query(offset=5, limit=5)
        self.assertEqual(ds.get_resource.call_count, 0)

        list(rl2)
        ds.get_resource.assert_called_with('/', params={
            'offset': 5,
            'limit': 5})

        self.assertEqual(rl2.offset, 5)
        self.assertEqual(rl2.limit, 5)

    def test_query_by_slicing(self):
        ds = MagicMock()
        ds.get_resource.return_value = {
            'href': '/',
            'offset': 2,
            'limit': 8,
            'size': 0,
            'items': []
        }

        rl = CollectionResource(client=MagicMock(data_store=ds), href='/')

        rl2 = rl[2:10]
        # data store needs to be caled once because we need the size property
        self.assertEqual(ds.get_resource.call_count, 1)

        list(rl2)
        ds.get_resource.assert_called_with('/', params={
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
            'size': 3,
            'items': [
                {'href': 'test/resource'},
                {'href': 'another/resource'},
                {'href': 'third/resource'}
            ]
        }

        rl = CollectionResource(client=MagicMock(data_store=ds), href='/')

        hrefs = [r.href for r in rl]

        self.assertEqual(hrefs, ['test/resource', 'another/resource',
            'third/resource'])

        ds.get_resource.assert_any_call('/', params=None)

        self.assertEqual(len(rl), 3)
        self.assertEqual(rl.offset, 2)
        self.assertEqual(rl.limit, 2)

    def test_creation_with_workflow_param_passing(self):
        ds = MagicMock()
        ds.create_resource.return_value = {
            'href': 'test/resource',
            'name': 'Test Resource',
        }

        rl = CollectionResource(
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

    def test_creation_with_expansion(self):
        ds = MagicMock()
        ds.create_resource.return_value = {
            'href': 'test/resource',
            'name': 'Test Resource',
        }

        rl = CollectionResource(
            client=MagicMock(data_store=ds,
                BASE_URL='http://www.example.com'),
            properties={
                'href': '/',
            })

        e = Expansion()
        e.add_property('bar', limit=5)

        rl.create({}, expand=e, some_param=True)

        ds.create_resource.assert_called_once_with('http://www.example.com/',
            {}, params={'someParam': True, 'expand': 'bar(limit:5)'})

    def test_get_single_app_by_indexing_and_get(self):
        ds = MagicMock()
        ds.get_resource.return_value = {
            'href': '/',
            'offset': 2,
            'limit': 25,
            'items': [
                {'href': 'test/resource'},
                {'href': 'another/resource'}
            ]
        }
        rl = CollectionResource(client=MagicMock(data_store=ds), properties={
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

    def test_tenant_expansion(self):
        e = Expansion()
        e.add_property('bar', limit=5)
        client = Client(api_key={'id': 'MyId', 'secret': 'Shush!'}, expand=e)

        self.assertIsInstance(client.tenant._expand, Expansion)

    def test_creation_with_sub_resources_sanitizes_their_attribs(self):
        ds = MagicMock()

        class SubRes(Resource):
            writable_attrs = ('foo_value',)

        class SubFixedAttrsDict(FixedAttrsDict):
            writable_attrs = ('attr_1', 'attr_2')

        class Res(Resource):
            writable_attrs = ('sub_resource', 'sub_fad')

            @staticmethod
            def get_resource_attributes():
                return {'sub_resource': SubRes, 'sub_fad': SubFixedAttrsDict}

        class ResList(CollectionResource):
            resource_class = Res

        rl = ResList(
            client=MagicMock(data_store=ds, BASE_URL='http://www.example.com'),
            properties={'href': '/'}
        )

        rl.create({
            'sub_resource': {'foo_value': 42},
            'sub_fad': {'attr_1': 1, 'attr_2': 2}
        })

        ds.create_resource.assert_called_once_with(
            'http://www.example.com/', {
                'subResource': {'fooValue': 42},
                'subFad': {'attr1': 1, 'attr2': 2}
            }, params={})

    def test_resource_refresh(self):
        ds = MagicMock()
        ds.get_resource.return_value = {
            'offset': 2,
            'limit': 8,
            'items': []
        }

        rl = CollectionResource(client=MagicMock(data_store=ds), href='/test_resources')

        rl.refresh()

        ds.uncache_resource.assert_called_once_with('/test_resources')


if __name__ == '__main__':
    main()


class TestFixedAttrsDict(TestCase):

    def test_fad_init(self):
        fad = FixedAttrsDict(MagicMock(), properties={'a': 1, 'b': 2})

        # getting a non-existing attribute is handled correctly
        with self.assertRaises(AttributeError):
            fad.a = 2
        # non-existing attribute access is handled correctly
        with self.assertRaises(AttributeError):
            fad.foo

    def test_getting_fad_property_names(self):
        fad = FixedAttrsDict(
            MagicMock(),
            properties={'href': 1, '_some_property': 2, 'some_property': 3})

        self.assertEqual(
            set(fad.__dict__.keys()),
            {'href', '_some_property', 'some_property'})

    def test_fad_dir_method(self):
        fad = FixedAttrsDict(
            MagicMock(),
            properties={'href': 1, '_some_property': 2, 'some_property': 3})

        self.assertEqual(
            {'href', '_some_property', 'some_property'}, set(fad.__dir__()))

    def test_sanitize_property(self):
        ret = FixedAttrsDict._sanitize_property({'full_name': 'full name'})
        self.assertEqual({'fullName': 'full name'}, ret)

    def test_wrapping_resource_attrs(self):
        r = FixedAttrsDict(MagicMock(), properties={})
        to_wrap = FixedAttrsDict(MagicMock(), properties={})
        ret = r._wrap_resource_attr(AgentConfig, to_wrap)
        self.assertEqual(to_wrap, ret)

        ret = r._wrap_resource_attr(AgentConfig, {'poll_interval': 60})
        self.assertEqual(60, ret.poll_interval)
        self.assertTrue(isinstance(ret, AgentConfig))

        ret = r._wrap_resource_attr(AgentConfig, None)
        self.assertIsNone(ret)

        self.assertRaises(
            TypeError, r._wrap_resource_attr, AgentConfig,
            'Unsupported Conversion')

    def test_getting_items_from_dict_mixing(self):
        r = AgentConfig(MagicMock(), properties={'poll_interval': 60})
        self.assertEqual([('poll_interval', 60)], r.items())

    def test_iter_method_on_dict_mixin(self):
        r = AgentConfig(MagicMock(), properties={'poll_interval': 60})
        self.assertEqual(['poll_interval'], list(r.__iter__()))

    def test_writable_attributes(self):

        class Fad(FixedAttrsDict):
            writable_attrs = ('name',)

        r = Fad(MagicMock(), properties={'name': 'Test',})

        r.name = 'foo'
        self.assertEqual(r.name, 'foo')

    def test_dict_attributes(self):

        class Fad(FixedAttrsDict):
            def get_dict_attributes(self):
                return {'related': FixedAttrsDict}

        r = Fad(MagicMock(), properties={
            'attr_1': 1,
            'related': {'attr_2': 2}
        })

        r2 = r.related

        self.assertTrue(isinstance(r2, FixedAttrsDict))
        self.assertEqual(r2.attr_2, 2)

__author__ = 'ecrisostomo'

from test.test_base import BaseTest
from stormpath.client import ApiKey
from stormpath.ds import DataStore
from stormpath.http import HttpClientRequestExecutor
from stormpath.resource import Resource

class ResourceTest(BaseTest):

    def test_dirty_property(self):

        props = {'href' : 'http://foo.com/test/123'}
        data_store = DataStore(HttpClientRequestExecutor(ApiKey('id', 'secret')))

        test_resource = TestResource(data_store, props)
        name = 'New Name'
        test_resource.name = name

        self.assertEquals(test_resource.name, name)

class TestResource(Resource):

    @property
    def name(self):
        return self._get_property_('name')

    @name.setter
    def name(self, name):
        self._set_property_('name', name)

    @property
    def description(self):
            return self._get_property_('description')

    @description.setter
    def description(self, description):
        self._set_property_('description', description)

    @property
    def password(self):
        return None

    @password.setter
    def password(self, password):
        self._set_property_('password', password)

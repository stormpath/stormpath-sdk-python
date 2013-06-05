#
# Copyright 2012, 2013 Stormpath, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from stormpath.util import assert_instance


class Base(object):

    HREF_PROP_NAME = 'href'

    def __init__(self, properties_or_url, client=None):

        if isinstance(properties_or_url, str):
            properties = {self.HREF_PROP_NAME: properties_or_url}
        elif isinstance(properties_or_url, dict):
            properties = properties_or_url
        else:
            raise ValueError("Please provide a url or a dictionary with properties")

        self.client = client
        self.properties = {}
        self.dirty_properties = {}
        self.set_properties(properties)
        self.dirty = False

    @property
    def data_store(self):
        return self.client.data_store

    def set_properties(self, properties):

        if (isinstance(properties, dict)):
            self.properties.update(properties)

            # Don't consider this resource materialized if it is only a reference.
            # A reference is any object that has only one 'href' property.
            href_only = len(self.properties) is 1 and self.HREF_PROP_NAME in self.properties
            self.materialized = not href_only

        else:
            self.materialized = False

    @property
    def property_names(self):
        return self.properties.copy().keys()

    def _get_href_from_dict(self, properties=None):
        if properties and assert_instance(properties, dict):
            return properties[self.HREF_PROP_NAME]

    def _get_property(self, name):

        if self.HREF_PROP_NAME is not name:
            #not the href/id, must be a property that requires materialization:
            if not self.new and not self.materialized:

                # only materialize if the property hasn't been set previously (no need to execute a server
                # request when we already have the most recent value):
                present = name in self.dirty_properties

                if not present:
                    self.materialize()

        return self._read_property(name)

    def _get_resource_property(self, name, cls):
        value = self._get_property(name)

        if(isinstance(value, dict)):
            href = value[self.HREF_PROP_NAME]

            if href:
                return self.data_store.instantiate(cls, value)

    def _get_resource_href_property(self, key):
        value = self._get_property(key)

        if isinstance(value, dict):
            return self._get_href_from_dict(key)
        else:
            return None

    def _set_property(self, name, value):
        self.properties[name] = value
        self.dirty_properties[name] = value
        self.dirty = True

    def materialize(self):
        cls = self.__class__

        resource = self.data_store.get_resource(self.href, cls)
        self.properties.update(resource.properties)

        #retain dirty properties:
        self.properties.update(self.dirty_properties)

        self.materialized = True

    @property
    def new(self):
        """
        Returns True if the resource doesn't yet have an assigned 'href' property,
        False otherwise.
        """

        #we can't call get_href in here, otherwise we'll have an infinite loop:
        return False if self._read_property(self.HREF_PROP_NAME) else True

    @property
    def href(self):
        return self._get_property(self.HREF_PROP_NAME)

    def _read_property(self, name):
        return self.properties[name] if name in self.properties else None


class Collection(Base):

    OFFSET = "offset"
    LIMIT = "limit"
    ITEMS = "items"
    items_iter = None

    @property
    def offset(self):
        return self._get_property(self.OFFSET)

    @property
    def limit(self):
        return self._get_property(self.LIMIT)

    def __iter__(self):
        return self

    def __next__(self):

        if self.items_iter:
            return next(self.items_iter)
        else:
            self.items_iter = iter(self._get_current_page().items)
            return next(self.items_iter)

    @property
    def item_type(self):
        """
        Children classes must return the InstanceResource classes
        (not an instance) that they hold as resources.
        i.e. AccountList should return the Account class.
        """
        pass

    def get(self, href):
        properties = self.data_store._execute_request('get', href, None)
        cls = self.item_type

        return self._to_resource(cls, properties)

    def create(self, properties_or_resource, property_name=None,
            href=None, cls=None):

        item_class = cls or self.item_type

        if isinstance(properties_or_resource, Base):
            resource = properties_or_resource

        else:
            resource = item_class(properties_or_resource, self.client)
            for k, v in properties_or_resource.items():
                setattr(resource, k, v)

        href = href or self._get_resource_href_property(property_name)

        return self.data_store.create(href, resource, item_class)

    def _get_current_page(self):

        value = self._get_property(self.ITEMS)
        items = self._to_resource_list(value)

        return Page(self.offset, self.limit, items)

    def _to_resource_list(self, values):

        cls = self.item_type
        items = list()

        if (values):
            for value in values:
                resource = self._to_resource(cls, value)
                items.append(resource)

        return items

    def _to_resource(self, cls, properties):
        return self.data_store.instantiate(cls, properties)


class Page(object):

    def __init__(self, offset, limit, items):
        self.offset = offset
        self.limit = limit
        self.items = items

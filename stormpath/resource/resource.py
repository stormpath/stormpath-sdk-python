__author__ = 'ecrisostomo'

from stormpath.resource.status import status_dict

class Resource:

    HREF_PROP_NAME = 'href'

    def __init__(self, data_store = None, properties = {}):
        self.data_store = data_store
        self.properties = {}
        self.dirty_properties = {}
        self.set_properties(properties)

    def set_properties(self, properties):
        self.properties.clear()
        self.dirty_properties.clear()
        self.dirty = False

        if (isinstance(properties, dict)):
            self.properties.update(properties)

            # Don't consider this resource materialized if it is only a reference.  A reference is any object that
            # has only one 'href' property.
            href_only = len(self.properties) is 1 and self.HREF_PROP_NAME in self.properties
            self.materialized = not href_only

        else:
            self.materialized = False

    def get_property(self, name):

        if self.HREF_PROP_NAME is not name:
            #not the href/id, must be a property that requires materialization:
            if not self.is_new() and not self.materialized:

                # only materialize if the property hasn't been set previously (no need to execute a server
                # request when we already have the most recent value):
                present = name in self.dirty_properties

                if not present:
                    self._materialize_()

        return self._read_property_(name)

    @property
    def property_names(self):
        return self.properties.keys()

    @property
    def href(self):
        return self.get_property(self.HREF_PROP_NAME)

    def _get_resource_property_(self, name, clazz):
        value = self.get_property(name)

        if(isinstance(value, dict)):
            href = value[self.HREF_PROP_NAME]

            if href:
                return self.data_store.instantiate(clazz, value)

    def _set_property_(self, name, value):
        self.properties[name] = value
        self.dirty_properties[name] = value
        self.dirty = True

    def _materialize_(self):
        clazz = self.__class__

        resource = self.data_store.get_resource(self.href(), clazz)
        self.properties.update(resource.properties)

        #retain dirty properties:
        self.properties.update(self.dirty_properties)

        self.materialized = True

    def is_new(self):
        """
        Returns True if the resource doesn't yet have an assigned 'href' property, False otherwise.
        """

        #we can't call get_href in here, otherwise we'll have an infinite loop:
        return False if self._read_property_(self.HREF_PROP_NAME) else True


    def _read_property_(self, name):
        return self.properties[name] if name in self.properties else None

class CollectionResource(Resource):

    OFFSET = "offset"
    LIMIT = "limit"
    ITEMS = "items"

    def __init__(self, data_store, properties):
        super().__init__(data_store, properties)
        self.index = 0

    @property
    def offset(self):
        return self.get_property(self.OFFSET)

    @property
    def limit(self):
        return self.get_property(self.LIMIT)

    def __iter__(self):
        return self

    def next(self):

        page = self._get_current_page()
        total_items = len(page.items)

        if self.index == total_items:
            raise StopIteration

        self.index += 1
        return page

    @property
    def item_type(self):
        """
        Children classes must return the InstanceResource classes (not an instance) that they hold as resources.
        i.e. AccountList should return the Account class.
        """
        pass

    def _get_current_page(self):

        value = self.get_property(self.ITEMS)
        items = self._to_resource_list_(value)

        return Page(self.offset, self.limit, items)

    def _to_resource_list_(self, values):

        clazz = self.item_type
        items = []

        if (values):
            for value in values:
                resource = self._to_resource_(clazz, value)
                items.append(resource)

        return items

    def _to_resource_(self, clazz, properties):
        return self.data_store.instantiate(clazz, properties)

class Page:

    def __init__(self, offset, limit, items):
        self.offset = offset
        self.limit = limit
        self.items = items

class InstanceResource(Resource):

    def save(self):
        self.data_store.save(self)

class StatusResource(Resource):

    STATUS = "status"

    @property
    def status(self):
        return status_dict[self.get_property(self.STATUS).upper()]

    @status.setter
    def status(self, status):
        self._set_property_(self.STATUS, str(status))

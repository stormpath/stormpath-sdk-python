__author__ = 'ecrisostomo'

from stormpath.resource.status import status_dict

class Resource:

    HREF_PROP_NAME = 'href'

    def __init__(self, data_store = None, properties = None):
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

    @property
    def property_names(self):
        return self.properties.copy().keys()

    @property
    def href(self):
        return self._get_property_(self.HREF_PROP_NAME)

    def _get_property_(self, name):

        if self.HREF_PROP_NAME is not name:
            #not the href/id, must be a property that requires materialization:
            if not self._is_new_() and not self.materialized:

                # only materialize if the property hasn't been set previously (no need to execute a server
                # request when we already have the most recent value):
                present = name in self.dirty_properties

                if not present:
                    self._materialize_()

        return self._read_property_(name)

    def _get_resource_property_(self, name, clazz):
        value = self._get_property_(name)

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

        resource = self.data_store.get_resource(self.href, clazz)
        self.properties.update(resource.properties)

        #retain dirty properties:
        self.properties.update(self.dirty_properties)

        self.materialized = True

    def _is_new_(self):
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
    items_iter = None

    @property
    def offset(self):
        return self._get_property_(self.OFFSET)

    @property
    def limit(self):
        return self._get_property_(self.LIMIT)

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
        Children classes must return the InstanceResource classes (not an instance) that they hold as resources.
        i.e. AccountList should return the Account class.
        """
        pass

    def _get_current_page(self):

        value = self._get_property_(self.ITEMS)
        items = self._to_resource_list_(value)

        return Page(self.offset, self.limit, items)

    def _to_resource_list_(self, values):

        clazz = self.item_type
        items = list()

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
        """
        Gets the status of the resource as a stormpath.resource.status.Enabled object or
        stormpath.resource.status.Disabled object.

        The string value of the object returned by this method can be obtained in one of two ways:

        1- Calling the *value* property of the object (assuming the *status_resource* variable is an instance of
        StatusResource):
            status_value = status_resource.status.value

        2- Calling the *str* function on the returned object (assuming the *status_resource* variable is an instance of
        StatusResource):
            status_value = str(status_resource.status)

        :returns the status of the resource as a stormpath.resource.status.Enabled object or
        stormpath.resource.status.Disabled object.
        """
        return status_dict[self._get_property_(self.STATUS).upper()]

    @status.setter
    def status(self, status):
        """
        Sets the status of the resource. The status can be set as a stormpath.resource.status.Enabled object, or
        stormpath.resource.status.Disabled object, or as a string (*ENABLED* or *DISABLED* are allowed).

        For example (assuming the *status_resource* variable is an instance of
        StatusResource):

        1- status_resource.status = stormpath.resource.status.disabled #or stormpath.resource.status.enabled

        OR

        2- status_resource.status = 'DISABLED' #or 'ENABLED'

        :param status: the status of the resource, as a stormpath.resource.status.Enabled object, or
        stormpath.resource.status.Disabled object, or as a string (*ENABLED* or *DISABLED* are allowed).
        """
        self._set_property_(self.STATUS, str(status))

__author__ = 'ecrisostomo'

from stormpath.resource.resource import Resource

class ResourceError(RuntimeError):

    def __init__(self, error):
        super().__init__(error.message if error else None)
        self.error = error

    @property
    def status(self):
        return self.error.status if self.error else -1

    @property
    def code(self):
        return self.error.code if self.error else -1

    @property
    def developer_message(self):
        return self.error.developer_message if self.error else None

    @property
    def more_info(self):
        return self.error.more_info if self.error else None

    @property
    def message(self):
        return self.error.message if self.error else None


class Error(Resource):

    STATUS = "status"
    CODE = "code"
    MESSAGE = "message"
    DEV_MESSAGE = "developerMessage"
    MORE_INFO = "moreInfo"

    def __init__(self, properties):
        super().__init__(properties=properties)

    @property
    def status(self):
        return self.get_property(Error.STATUS)

    @property
    def code(self):
        return self.get_property(Error.CODE)

    @property
    def message(self):
        return self.get_property(Error.MESSAGE)

    @property
    def developer_message(self):
        return self.get_property(Error.DEV_MESSAGE)

    @property
    def more_info(self):
        return self.get_property(Error.MORE_INFO)

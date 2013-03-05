__author__ = 'ecrisostomo'

from stormpath.resource.resource import Resource

class ResourceError(RuntimeError):

    def __init__(self, error):
        super().__init__(error.message() if error else '')
        self.error = error

    def status(self):
        return self.error.status() if self.error else -1

    def code(self):
        return self.error.code() if self.error else -1

    def developer_message(self):
        return self.error.developer_message() if self.error else None

    def more_info(self):
        return self.error.more_info() if self.error else None


class Error(Resource):

    STATUS = "status"
    CODE = "code"
    MESSAGE = "message"
    DEV_MESSAGE = "developerMessage"
    MORE_INFO = "moreInfo"

    def __init__(self, properties):
        super().__init__(properties=properties)

    def status(self):
        self.get_property(Error.STATUS)

    def code(self):
        self.get_property(Error.CODE)

    def message(self):
        self.get_property(Error.MESSAGE)

    def developer_message(self):
        self.get_property(Error.DEV_MESSAGE)

    def more_info(self):
        self.get_property(Error.MORE_INFO)

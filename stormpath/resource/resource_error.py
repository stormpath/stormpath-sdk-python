__author__ = 'ecrisostomo'

from stormpath.resource.resource import Resource

STATUS = "status"
CODE = "code"
MESSAGE = "message"
DEV_MESSAGE = "developerMessage"
MORE_INFO = "moreInfo"

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

    def __init__(self, properties):
        super().__init__(None, properties)

    def status(self):
        self.get_property(STATUS)

    def code(self):
        self.get_property(CODE)

    def message(self):
        self.get_property(MESSAGE)

    def developer_message(self):
        self.get_property(DEV_MESSAGE)

    def more_info(self):
        self.get_property(MORE_INFO)

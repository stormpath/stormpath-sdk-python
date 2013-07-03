class Error(RuntimeError):
    def __init__(self, error):
        super(Error, self).__init__(error.get('developerMessage'))
        self.error = error

    @property
    def status(self):
        return self.error.get('status', -1)

    @property
    def code(self):
        return self.error.get('code', -1)

    @property
    def developer_message(self):
        return self.error.get('developer_message')

    @property
    def more_info(self):
        return self.error.get('more_info')

    @property
    def message(self):
        return self.error.get('message')

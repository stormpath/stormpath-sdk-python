class DataStore(object):

    def __init__(self, executor):
        self.executor = executor

    def get_resource(self, href, params=None):
        return self.executor.get(href, params=params)

    def create_resource(self, href, data, params=None):
        return self.executor.post(href, data, params=params)

    def update_resource(self, href, data):
        return self.executor.post(href, data)

    def delete_resource(self, href):
        return self.executor.delete(href)

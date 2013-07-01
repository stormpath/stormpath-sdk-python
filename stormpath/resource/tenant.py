from .base import Resource
#from .error import Error as StormpathError

class Tenant(Resource):
    path = 'tenants'
    fields = ['name', 'key']
    related_fields = ['applications', 'directories']

    def read(self):
        if self._data:
            return

        params = {}
        if self._expansion:
            params.update({'expand': self._expansion.params})

        resp = self._session.get(self.url, params=params, allow_redirects=False)

        if resp.status_code == 302:
            self.url = resp.headers['location']
            return self.read()

        if resp.status_code != 200:
            #raise StormpathError(resp.json())
            raise Exception(resp.json())

        self._data = resp.json()

from .base import Resource
from ..error import Error

class Tenant(Resource):
    """
    Tenant resource:
    https://www.stormpath.com/docs/rest/api#Tenants

    """

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
            raise Error(resp.json())

        self._data = resp.json()

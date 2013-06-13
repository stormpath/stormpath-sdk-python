from .auth import Auth
from .resource import Resource, ResourceList
from .resource import Tenant
from .resource import Application
from .resource import Directory

class Client(object):
    def __init__(self, **kwargs):
        self.auth = Auth(**kwargs)
        self._tenant = None

    def _get_tenant(self):
        if not self._tenant:
            self._tenant = Tenant(auth=self.auth, id='current')
        return self._tenant

    @property
    def tenant(self):
        return self._get_tenant()

    @property
    def applications(self):
        url = self._get_tenant().applications.get('href')
        return ResourceList(url=url, auth=self.auth, resource=Application)

    @property
    def directories(self):
        url = self._get_tenant().directories.get('href')
        return ResourceList(url=url, auth=self.auth, resource=Directory)

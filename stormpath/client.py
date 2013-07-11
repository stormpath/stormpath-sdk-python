from .auth import Auth
from .resource import Resource, ResourceList
from .resource import Tenant
from .resource import Application, ApplicationResourceList
from .resource import Directory

class Client(object):
    """
    Client is the main entry point for consuming Stormpath REST API.
    It takes care of setting up authentication/session and provides
    access to Stormpath resources.

    Resources:
    https://www.stormpath.com/docs/rest/api#Resources

    """
    def __init__(self, **kwargs):
        self.auth = Auth(**kwargs)
        self._tenant = None

    def _get_tenant(self):
        if not self._tenant:
            self._tenant = Tenant(auth=self.auth, id='current')
        return self._tenant

    @property
    def tenant(self):
        """
        Returns current tenant used by Client to find related resources.

        https://www.stormpath.com/docs/rest/api#Tenants

        """
        return self._get_tenant()

    @property
    def applications(self):
        """
        Returns applications related to current tenant used by Client.

        https://www.stormpath.com/docs/rest/api#Applications

        """
        url = self._get_tenant().applications.get('href')
        return ApplicationResourceList(url=url, auth=self.auth, resource=Application)

    @property
    def directories(self):
        """
        Returns directories related to current tenant used by Client.

        https://www.stormpath.com/docs/rest/api#Directories

        """
        url = self._get_tenant().directories.get('href')
        return ResourceList(url=url, auth=self.auth, resource=Directory)

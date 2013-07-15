from .auth import Auth
from .resource import ResourceList
from .resource import Tenant
from .resource import Application, ApplicationResourceList
from .resource import Directory
from .resource import Account
from .resource import Group
from .resource import API_URL

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

    @property
    def accounts(self):
        """
        Returns accounts related to current tenant used by Client.

        https://www.stormpath.com/docs/rest/api#Accounts

        """
        # The API doesn't return the accounts URL along with the Tenant.
        # If the SDK user wants to access an account regardless of directory
        # or application, he/she has to follow a direct url but we still have to
        # create the Tenant to access applications and directories.
        self._get_tenant()
        url = '%s%s' % (API_URL, "accounts")
        return ResourceList(url=url, auth=self.auth, resource=Account)

    @property
    def groups(self):
        """
        Returns groups related to current tenant used by Client.

        https://www.stormpath.com/docs/rest/api#Groups

        """
        # The API doesn't return the accounts URL along with the Tenant.
        # If the SDK user wants to access an account regardless of directory
        # or application, he/she has to follow a direct url but we still have to
        # create the Tenant to access applications and directories.
        self._get_tenant()
        url = '%s%s' % (API_URL, "groups")
        return ResourceList(url=url, auth=self.auth, resource=Group)

from . import Resource, ResourceList

class Directory(Resource):
    """
    Directory resource:
    https://www.stormpath.com/docs/rest/api#Directories

    """

    path = 'directories'
    fields = ['name', 'description', 'status']
    related_fields = ['accounts', 'groups']

    def __str__(self):
        return self.name

    @property
    def tenant(self):
        """
        Returns a Tenant related to this directory.

        """
        from .tenant import Tenant
        return Tenant(session=self._session, url=self._data['tenant']['href'])

    def create_account(self, account_data):
        """
        Creates and returns a new Account related to this directory.

        """
        return self.accounts.create(account_data)

    def create_group(self, group_data):
        """
        Creates and returns a new Group related to this directory.

        """
        group = self.groups.create(group_data)
        return group

    @property
    def accounts(self):
        """
        Returns a AccountResourceList related to this directory.

        """

        from .account import Account, AccountResourceList

        if not self._data:
            self.read()

        url = self._data['accounts']['href']
        if 'accounts' in self._expansion.items.keys():
            data = self._data['accounts']['items']
            return AccountResourceList(url=url, session=self._session,\
                    resource=Account, directory=self, data=data)

        return AccountResourceList(url=url, session=self._session,\
                resource=Account, directory=self)

    @property
    def groups(self):
        """
        Returns a GroupResourceList related to this directory.

        """
        from .group import Group, GroupResourceList

        if not self._data:
            self.read()

        url = self._data['groups']['href']
        return GroupResourceList(url=url, session=self._session,\
                resource=Group, directory=self)

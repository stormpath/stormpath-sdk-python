from . import Resource, ResourceList

class Directory(Resource):
    path = 'directories'
    fields = ['name', 'description', 'status']

    def __str__(self):
        return self.name

    @property
    def tenant(self):
        from .tenant import Tenant
        return Tenant(session=self._session, url=self._data['tenant'])

    def create_account(self, account_data):
        return self.accounts.create(account_data)

    def create_group(self, group_data):
        group = self.groups.create(group_data)
        return group

    @property
    def accounts(self):
        from .account import Account, AccountResourceList

        if not self._data:
            self.read()

        url = self._data['accounts']['href']
        return AccountResourceList(url=url, session=self._session,\
                resource=Account, directory=self)

    @property
    def groups(self):
        from .group import Group, GroupResourceList

        if not self._data:
            self.read()

        url = self._data['groups']['href']
        return GroupResourceList(url=url, session=self._session,\
                resource=Group, directory=self)

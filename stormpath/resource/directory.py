from . import (Resource, ResourceList,
        Account, AccountResourceList,
        Group, GroupResourceList)

class Directory(Resource):
    path = 'directories'
    fields = ['name', 'description', 'status']

    def __str__(self):
        return self.name

    @property
    def accounts(self):
        if not self._data:
            self.read()

        url = self._data['accounts']['href']
        return AccountResourceList(url=url, session=self._session, resource=Account, directory=self)

    @property
    def groups(self):
        if not self._data:
            self.read()

        url = self._data['groups']['href']
        return GroupResourceList(url=url, session=self._session, resource=Group, directory=self)

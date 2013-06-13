import json
import requests
from . import Resource, ResourceList, API_URL

class Account(Resource):
    path = 'accounts'
    fields = ['username', 'email', 'password', 'givenName',
            'middleName', 'surname', 'status',]

    def __str__(self):
        return self.username

class AccountResourceList(ResourceList):
    def __init__(self, *args, **kwargs):
        if 'directory' in kwargs.keys():
            self._directory = kwargs.pop('directory')

        if 'group' in kwargs.keys():
            self._group = kwargs.pop('group')

        super(AccountResourceList, self).__init__(*args, **kwargs)

    def create(self, data):
        if self._directory:
            # handle creation in directory
            url = '%sdirectories/%s/accounts' % (API_URL, self._directory.uid)
            resp = self._session.post(url, data=json.dumps(data))
            if resp.status_code != 200:
                raise NotImplementedError

            account = Account(session=self._session, data=resp.json())
            return account
        else:
            raise NotImplementedError

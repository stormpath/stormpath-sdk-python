import json
import requests
from .base import Resource, ResourceList, API_URL
from .directory import Directory

class Group(Resource):
    path = 'groups'
    fields = ['name', 'description', 'status',]

    def __str__(self):
        return self.name

    @property
    def tenant(self):
        from .tenant import Tenant
        return Tenant(session=self._session, url=self._data['tenant']['href'])

    @property
    def directory(self):
        self.read()
        url = self._data['directory']['href']
        directory = Directory(session=self._session, url=url)
        directory.read()
        return directory

    @property
    def accounts(self):
        from .account import Account, AccountResourceList
        if not self._data:
            self.read()

        url = self._data['accounts']['href']
        return AccountResourceList(url=url, session=self._session,\
                resource=Account, group=self)

    def add_account(self, account):
        from .group_membership import GroupMembership
        gm = GroupMembership(session=self._session, account=account, group=self)
        gm.save()
        return gm

class GroupResourceList(ResourceList):
    def __init__(self, *args, **kwargs):
        if 'directory' in kwargs:
            self._directory = kwargs.pop('directory')

        super(GroupResourceList, self).__init__(*args, **kwargs)

    def create(self, *args, **kwargs):
        if len(args) == 1:
            data = args[0]
        else:
            data = kwargs.get('data') or kwargs

        url = '%sdirectories/%s/groups' % (API_URL, self._directory.uid)
        resp = self._session.post(url, data=json.dumps(data))
        if resp.status_code not in (200, 201):
            raise NotImplementedError

        return Group(session=self._session, data=resp.json())

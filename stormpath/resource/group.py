from .base import Resource, ResourceList

class Group(Resource):
    path = 'groups'
    fields = ['name', 'description', 'status',]

    def __str__(self):
        return self.name

    @property
    def accounts(self):
        url = self._data['accounts']['href']
        return AccountResourceList(url=url, auth=self.auth, resource=Account, group=self)

    def add_account(self, account):
        url = '%sgroupMemberships' % API_URL
        data = {
            'account': {'href': account.url},
            'group': {'href': self.url},
        }
        resp = requests.post(url, auth=self.auth.basic,\
                data=json.dumps(data), headers=self.headers)
        if resp.status_code != 201:
            raise NotImplementedError

        #self._data = json.loads(resp.text)

class GroupResourceList(ResourceList):
    def __init__(self, *args, **kwargs):
        self._directory = kwargs.pop('directory')
        super(GroupResourceList, self).__init__(*args, **kwargs)

    def create(self, data):
        url = '%sdirectories/%s/groups' % (API_URL, self._directory.uid)
        resp = requests.post(url, auth=self._auth.basic,\
                data=json.dumps(data), headers=self.headers)
        if resp.status_code != 201:
            raise NotImplementedError

        #self._data = json.loads(resp.text)

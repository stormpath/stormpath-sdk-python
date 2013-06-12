import json
import jprops
import base64
import requests
from requests.auth import HTTPBasicAuth, HTTPDigestAuth

API_URL = 'https://api.stormpath.com/v1/'

class Auth(object):
    def __init__(self, **kwargs):
        self._key = None
        self._secret = None

        path = kwargs.get('api_key_file_location', None)
        if path:
            with open(path, 'r') as fp:
                cred = jprops.load_properties(fp)
                self._key = cred.get('apiKey.id')
                self._secret = cred.get('apiKey.secret')
                del cred
            return

        api_key = kwargs.get('api_key')
        if api_key:
            if type(api_key) == dict:
                self._key = api_key.get('id')
                self._secret = api_key.get('secret')
            else:
                self._key = api_key.id
                self._secret = api_key.secret
            return

        # add other auth sources
        raise Exception('other auth sources not yet implemented')

    def __call__(self):
        return self.basic

    # added to satisfy tests, should be removed
    def get(self, name):
        pass

    @property
    def id(self):
        return self._key

    @property
    def secret(self):
        return self._secret

    @property
    def basic(self):
        return HTTPBasicAuth(self._key, self._secret)

    @property
    def digest(self):
        raise NotImplementedError
        # not http digest alg.
        # return HTTPDigestAuth(self._key, self._secret)

class Resource(object):
    def __init__(self, **kwargs):
        self._uid = None
        self._is_dirty = False
        self.fields = getattr(self, 'fields', [])
        self.related_fields = getattr(self, 'related_fields', [])
        self.headers = {'content-type': 'application/json'}
        self.auth = kwargs.pop('auth')

        self._data = kwargs.get('data')
        if self._data:
            self.url = self._data.get('href')
            if self.url:
                return

        self.url = kwargs.get('url')
        if not self.url:
            id = kwargs.get('id')
            if id:
                path = '%s/%s' % (self.path, id)
                self.url = '%s%s' % (API_URL, path)

    def __repr__(self):
        try:
            return "%s: %s" % (self.__class__.__name__, str(self))
        except:
            return self.__class__.__name__

    def __str__(self):
        return self.url

    @property
    def href(self):
        if self.url:
            return self.url

        raise Exception('Resource not saved, href is not available.')

    @property
    def uid(self):
        if self.url:
            uid = self.url[self.url.rfind('/')+1:]
            return uid
        raise Exception('Resource not saved, unique identifier is not available.')

    def create(self):
        url = '%s%s' % (API_URL, self.path)
        resp = requests.post(url, auth=self.auth.basic, headers=self.headers, data=json.dumps(self._data))
        if resp.status_code != 201:
            raise NotImplementedError

        self._data = json.loads(resp.text)

    def read(self):
        if self._data:
            return

        resp = requests.get(self.url, headers=self.headers, auth=self.auth.basic, data=json.dumps({}))
        if resp.status_code != 200:
            raise NotImplementedError

        self._data = json.loads(resp.text)

    def update(self):
        data = {k: v for k,v in self._data.items() if k in self.fields}
        resp = requests.post(self.url, auth=self.auth.basic, headers=self.headers, data=json.dumps(data))
        if resp.status_code != 200:
            raise NotImplementedError

        self._data = json.loads(resp.text)

    def delete(self):
        pass

    def save(self):
        # fixme: check if saving new or existing object, check if dirty for update
        self.update()

    def __dir__(self):
        return self.fields

    def __getattr__(self, name):
        data = self.__dict__.get('_data')
        fields = self.__dict__.get('fields', [])
        related_fields = self.__dict__.get('related_fields', [])

        if name in fields or name in related_fields:
            if not data and 'url' in self.__dict__:
                self.read()
                data = self.__dict__.get('_data')

            if data and name in data:
                return data[name]

        raise AttributeError

    def __setattr__(self, name, value):
        data = self.__dict__.get('_data')
        fields = self.__dict__.get('fields', [])

        if data and name in fields:
            data[name] = value
            object.__setattr__(self, '_is_dirty', True)
        else:
            object.__setattr__(self, name, value)

class ResourceList(object):
    def __init__(self, *args, **kwargs):
        self._auth = kwargs.pop('auth')
        self._resource_class = kwargs.pop('resource')
        self._url = kwargs.pop('url')
        self.headers = {'content-type': 'application/json'}
        self._items = None
        super(ResourceList, self).__init__(*args, **kwargs)

    def get(self, url):
        resp = self._resource_class(auth=self._auth, url=url)
        return resp

    def create(self, data):
        r = self._resource_class(auth=self._auth, data=data)
        r.create()

    def __getitem__(self, key):
        resp = requests.get(self._url, auth=self._auth.basic, headers=self.headers, data=json.dumps({}))
        if resp.status_code != 200:
            raise NotImplementedError

        data = json.loads(resp.text)
        item = data['items'][key]
        return self._resource_class(auth=self._auth, data=item)

    def __iter__(self):
        # fixme: implement pagination and cache
        if not self._items:
            resp = requests.get(self._url, auth=self._auth.basic, headers=self.headers, data=json.dumps({}))
            if resp.status_code != 200:
                raise NotImplementedError

            self._items = []
            data = json.loads(resp.text)
            for item in data['items']:
                m = self._resource_class(auth=self._auth, data=item)
                self._items.append(m)
            self._items = self._items
        while self._items:
            yield self._items.pop(0)
            # if not self._items check next resource page/collection
        else:
            raise StopIteration

class DirectoryResourceList(ResourceList):
    pass

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
            resp = requests.post(url, auth=self._auth.basic,\
                    data=json.dumps(data), headers=self.headers)
            if resp.status_code != 201:
                raise NotImplementedError

            #self._data = json.loads(resp.text)
        else:
            raise NotImplementedError

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

class Tenant(Resource):
    path = 'tenants'
    fields = ['name', 'key']
    related_fields = ['applications', 'directories']

class Application(Resource):
    path = 'applications'
    fields = ['name', 'description', 'status',]

    def __str__(self):
        return self.name

    def authenticate_account(self, login, password):
        value = '%s:%s' % (login, password)
        value = base64.b64encode(value.encode()).decode()

        path = 'applications/%s/loginAttempts'
        url = "%s%s" % (API_URL, path % self.uid)

        resp = requests.post(url=url, auth=self.auth.basic, headers=self.headers,\
                data=json.dumps({'type': 'basic', 'value': value}))
        if resp.status_code != 200:
            raise NotImplementedError

        try:
            account_url = json.loads(resp.text).get('account').get('href')
        except:
            # unknown exception
            raise NotImplementedError

        account = Account(auth=self.auth, url=account_url)
        account.read()
        return account

    def send_password_reset_email(self, email):
        path = 'applications/%s/passwordResetTokens'
        url = "%s%s" % (API_URL, path % self.uid)

        resp = requests.post(url=url, auth=self.auth.basic, headers=self.headers,\
                data=json.dumps({'email': email}))
        if resp.status_code != 200:
            raise NotImplementedError

        try:
            account_url = json.loads(resp.text).get('account').get('href')
        except:
            # unknown exception
            raise NotImplementedError

        account = Account(auth=self.auth, url=account_url)
        account.read()
        return account

class Directory(Resource):
    path = 'directories'
    fields = ['name', 'description', 'status']

    def __str__(self):
        return self.name

    @property
    def accounts(self):
        url = self._data['accounts']['href']
        return AccountResourceList(url=url, auth=self.auth, resource=Account, directory=self)

    @property
    def groups(self):
        url = self._data['groups']['href']
        return GroupResourceList(url=url, auth=self.auth, resource=Group, directory=self)

class Account(Resource):
    path = 'accounts'
    fields = ['username', 'email', 'password', 'givenName',
            'middleName', 'surname', 'status',]

    def __str__(self):
        return self.username

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


class Client(object):
    def __init__(self, **kwargs):
        self.headers = {'content-type': 'application/json'}
        self._auth = Auth(**kwargs)
        self._tenant = None

    def _get_tenant(self):
        if not self._tenant:
            self._tenant = Tenant(auth=self._auth, id='current')
        return self._tenant

    @property
    def auth(self):
        return self._auth

    @property
    def api_key(self):
        return self._auth

    @property
    def tenant(self):
        return self._get_tenant()

    @property
    def applications(self):
        url = self._get_tenant().applications.get('href')
        return ResourceList(url=url, auth=self._auth, resource=Application)

        resp = requests.get(url, auth=self._auth.basic, headers=self.headers, data=json.dumps({}))
        if resp.status_code != 200:
            raise NotImplementedError

        items = ResourceList(auth=self._auth, resource=Application)
        data = json.loads(resp.text)
        for item in data['items']:
            items.append(Application(auth=self._auth, data=item))

        return items

    @property
    def directories(self):
        url = self._get_tenant().directories.get('href')
        return ResourceList(url=url, auth=self._auth, resource=Directory)

        resp = requests.get(url, auth=self._auth.basic, headers=self.headers, data=json.dumps({}))
        if resp.status_code != 200:
            raise NotImplementedError

        items = ResourceList(auth=self._auth, resource=Directory)
        data = json.loads(resp.text)
        for item in data['items']:
            items.append(Directory(auth=self._auth, data=item))

        return items

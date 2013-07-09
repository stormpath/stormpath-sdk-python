import base64
import requests
import json
from . import Resource, ResourceList, API_URL
from . import Account, AccountResourceList
from . import Group, GroupResourceList
from ..error import Error as StormpathError

class Application(Resource):
    """
    Application resource:
    https://www.stormpath.com/docs/rest/api#Applications

    """

    path = 'applications'
    fields = ['name', 'description', 'status',]

    def __str__(self):
        return self.name

    @property
    def tenant(self):
        """
        Returns a Tenant related to this application.

        """

        from .tenant import Tenant
        return Tenant(session=self._session, url=self._data['tenant']['href'])

    @property
    def accounts(self):
        """
        Returns a AccountResourceList related to this application.

        """

        if not self._data:
            self.read()

        url = self._data['accounts']['href']
        return AccountResourceList(url=url, session=self._session,\
                resource=Account)

    @property
    def groups(self):
        """
        Returns a GroupResourceList related to this application.

        """

        if not self._data:
            self.read()

        url = self._data['groups']['href']
        return GroupResourceList(url=url, session=self._session,\
                resource=Group)

    @property
    def token(self):
        return self.password_reset_token

    def create(self, create_directory=None):
        """
        Creates a new Application.

        https://www.stormpath.com/docs/rest/api#CreatingResources

        """

        params = {}
        url = '%s%s' % (API_URL, self.path)
        if create_directory is not None:
            params = {'createDirectory': create_directory}

        resp = self._session.post(url, data=json.dumps(self._data),
            params=params)

        if resp.status_code not in (200, 201):
            raise StormpathError(resp.json())

        self._data = resp.json()

    def authenticate_account(self, login, password):
        """
        Allows an application to authenticate its associated accounts.

        https://www.stormpath.com/docs/rest/api#ApplicationLoginAttempts

        """

        value = '%s:%s' % (login, password)
        value = base64.b64encode(value.encode()).decode()

        path = 'applications/%s/loginAttempts'
        url = "%s%s" % (API_URL, path % self.uid)

        resp = self._session.post(url=url, data=json.dumps({'type': 'basic', 'value': value}))
        if resp.status_code != 200:
            raise StormpathError(resp.json())

        try:
            account_url = json.loads(resp.text).get('account').get('href')
        except:
            # unknown exception
            raise NotImplementedError

        account = Account(session=self._session, url=account_url)
        account.read()
        return account

    def send_password_reset_email(self, email):
        """
        Initiates password reset workflow:
        https://www.stormpath.com/docs/rest/api#SetApplicationPWResetTokenProperties

        """

        path = 'applications/%s/passwordResetTokens'
        url = "%s%s" % (API_URL, path % self.uid)

        resp = self._session.post(url=url, data=json.dumps({'email': email}))
        if resp.status_code != 200:
            raise StormpathError(resp.json())

        try:
            token = json.loads(resp.text).get('href').split('/')[-1]
        except:
            # FIXME: unknown exception
            raise NotImplementedError

        try:
            account_url = json.loads(resp.text).get('account').get('href')
        except:
            # FIXME: unknown exception
            raise NotImplementedError

        account = Account(session=self._session, url=account_url)
        account.read()
        account.password_reset_token = token
        return account

    def verify_password_reset_token(self, token):
        """
        Validates password reset token:
        https://www.stormpath.com/docs/rest/api#ReadPWResetToken

        """
        path = 'applications/%s/passwordResetTokens/%s' % (self.uid, token)
        url = "%s%s" % (API_URL, path)

        resp = self._session.get(url=url)
        if resp.status_code != 200:
            raise StormpathError(resp.json())

        try:
            account_url = json.loads(resp.text).get('account').get('href')
        except:
            # FIXME: unknown exception
            raise NotImplementedError

        account = Account(session=self._session, url=account_url)
        account.read()
        return account

class ApplicationResourceList(ResourceList):
    """
    List of application resources.

    """

    def create(self, *args, **kwargs):
        dirname = kwargs.get('create_directory', None)

        if len(args) == 1:
            data = args[0]
        else:
            data = kwargs.get('data') or kwargs
        r = self._resource_class(session=self._session, data=data)
        r.create(create_directory=dirname)
        return r

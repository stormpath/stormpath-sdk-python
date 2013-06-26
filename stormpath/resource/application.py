import base64
import requests
import json
from . import Resource, API_URL
from . import Account, AccountResourceList
from . import Group, GroupResourceList
from ..error import Error as StormpathError

class Application(Resource):
    path = 'applications'
    fields = ['name', 'description', 'status',]

    def __str__(self):
        return self.name

    @property
    def tenant(self):
        from .tenant import Tenant
        return Tenant(session=self._session, url=self._data['tenant']['href'])

    @property
    def accounts(self):
        if not self._data:
            self.read()

        url = self._data['accounts']['href']
        return AccountResourceList(url=url, session=self._session,\
                resource=Account)

    @property
    def groups(self):
        if not self._data:
            self.read()

        url = self._data['groups']['href']
        return GroupResourceList(url=url, session=self._session,\
                resource=Group)

    def authenticate_account(self, login, password):
        value = '%s:%s' % (login, password)
        value = base64.b64encode(value.encode()).decode()

        path = 'applications/%s/loginAttempts'
        url = "%s%s" % (API_URL, path % self.uid)

        resp = self._session.post(url=url, data=json.dumps({'type': 'basic', 'value': value}))
        if resp.status_code != 200:
            raise NotImplementedError

        try:
            account_url = json.loads(resp.text).get('account').get('href')
        except:
            # unknown exception
            raise NotImplementedError

        account = Account(session=self._session, url=account_url)
        account.read()
        return account

    def send_password_reset_email(self, email):
        path = 'applications/%s/passwordResetTokens'
        url = "%s%s" % (API_URL, path % self.uid)

        resp = self._session.post(url=url, data=json.dumps({'email': email}))
        if resp.status_code != 200:
            raise NotImplementedError

        try:
            account_url = json.loads(resp.text).get('account').get('href')
        except:
            # FIXME: unknown exception
            raise NotImplementedError

        account = Account(session=self._session, url=account_url)
        account.read()
        return account

    def verify_password_reset_token(self, token):
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

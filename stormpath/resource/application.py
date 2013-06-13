import base64
import requests
import json
from . import Resource, API_URL
from . import Account

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

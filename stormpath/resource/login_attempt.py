from base64 import b64encode
from .base import Resource, ResourceList


class LoginAttempt(Resource):
    readwrite_attrs = ('type', 'value')

    def get_resource_attributes(self):
        from .account import Account
        return {
            'account': Account
        }


class LoginAttemptList(ResourceList):
    resource_class = LoginAttempt

    def basic_auth(self, login, password):
        return self.create({
            'type': 'basic',
            'value': b64encode(login + ':' + password)
        })

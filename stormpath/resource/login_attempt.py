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
        value = login + ':' + password

        if issubclass(bytes, str):
            value = b64encode(value)
        else:
            value = b64encode(value.encode('utf-8')).decode('ascii')

        return self.create({
            'type': 'basic',
            'value': value
        })

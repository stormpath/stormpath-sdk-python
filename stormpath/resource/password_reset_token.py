from .base import Resource, ResourceList


class PasswordResetToken(Resource):
    readwrite_attrs = ('email',)

    def get_resource_attributes(self):
        from .account import Account
        return {
            'account': Account
        }

    @property
    def token(self):
        return self.href.split('/')[-1]


class PasswordResetTokenList(ResourceList):
    resource_class = PasswordResetToken

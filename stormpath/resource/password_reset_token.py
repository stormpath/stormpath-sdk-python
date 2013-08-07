"""
Handles reset tokens used in password reset workflow.

More info in documentation:
https://www.stormpath.com/docs/rest/product-guide#PasswordReset
"""

from .base import Resource, ResourceList


class PasswordResetToken(Resource):
    writable_attrs = ('email',)

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

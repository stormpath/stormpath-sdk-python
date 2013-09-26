from .base import Resource, CollectionResource


class PasswordResetToken(Resource):
    """Handles reset tokens used in password reset workflow.

    More info in documentation:
    https://www.stormpath.com/docs/rest/product-guide#PasswordReset

    Attributes:

    :py:attr:`token` - Token with which to reset the password.

    """

    writable_attrs = ('email',)

    def get_resource_attributes(self):
        from .account import Account
        return {
            'account': Account
        }

    @property
    def token(self):
        return self.href.split('/')[-1]


class PasswordResetTokenList(CollectionResource):
    """List of reset tokens.
    """
    resource_class = PasswordResetToken

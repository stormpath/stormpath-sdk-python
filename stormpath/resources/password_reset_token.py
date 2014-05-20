"""Stormpath PasswordResetToken resource mappings."""


from .base import (
    CollectionResource,
    Resource,
)


class PasswordResetToken(Resource):
    """Handles reset tokens used in password reset workflow.

    More info in documentation:
    http://docs.stormpath.com/rest/product-guide/#reset-an-accounts-password

    Attributes:

    :py:attr:`token` - Token with which to reset the password.
    """
    writable_attrs = ('email',)

    @staticmethod
    def get_resource_attributes():
        from .account import Account

        return {
            'account': Account
        }

    @property
    def token(self):
        return self.href.split('/')[-1]


class PasswordResetTokenList(CollectionResource):
    """List of reset tokens."""
    resource_class = PasswordResetToken

    def build_reset_href(self, token):
        return self._get_create_path() + ('/%s' % token.token)

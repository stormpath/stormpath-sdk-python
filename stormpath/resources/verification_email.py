"""Stormpath VerificationEmail resource mappings."""

from .account import Account
from .base import (
    CollectionResource,
    Resource,
)


class VerificationEmail(Resource):
    pass


class VerificationEmailList(CollectionResource):
    """List of email verfication requests."""
    resource_class = VerificationEmail

    def _ensure_data(self):
        raise ValueError("It is not possible to access verification_emails!")

    def resend(self, account=None, account_store=None):
        """Resend the Email Verification Token.

        :param account:  An :class:`stormpath.resources.account.Account`
        :param account_store: A :class:`stormpath.resources.directory.Directory` or :class:`stormpath.resources.group.Group`.
        """
        if account is None or account_store is None:
            raise ValueError('You must specify the Account and Account Store')

        if isinstance(account_store, Resource):
            account_store = account_store.href

        if isinstance(account, Account):
            account = account.email

        data = self._store.create_resource(self._get_create_path(), {
            'login': account,
            'account_store': account_store
        })

        return self.resource_class(client=self._client, properties=data)


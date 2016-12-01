"""Stormpath AccountLinks resource mappings."""

from .base import (
    CollectionResource,
    DeleteMixin,
    DictMixin,
    Resource
)


class AccountLink(Resource, DictMixin, DeleteMixin):
    writable_attrs = (
        'left_account',
        'right_account'
    )

    @staticmethod
    def get_resource_attributes():
        from .account import Account

        return {
            'left_account': Account,
            'right_account': Account
        }


class AccountLinkList(CollectionResource):
    """AccountLink resource list."""
    resource_class = AccountLink

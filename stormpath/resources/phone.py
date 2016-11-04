"""Stormpath Factors resource mappings."""

from .base import (
    CollectionResource,
    DeleteMixin,
    DictMixin,
    Resource,
    SaveMixin,
    StatusMixin,
)


class Phone(Resource, DeleteMixin, DictMixin, SaveMixin, StatusMixin):
    """
    Stormpath Phone resource.
    """

    writable_attrs = ('number', )

    @staticmethod
    def get_resource_attributes():
        from .account import Account

        return {
            'account': Account
        }


class PhoneList(CollectionResource):
    """Phone resource list."""
    resource_class = Phone

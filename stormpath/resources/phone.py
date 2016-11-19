"""Stormpath Factors resource mappings."""

from .base import CollectionResource, DeleteMixin, DictMixin, Resource, SaveMixin, StatusMixin


class Phone(Resource, DeleteMixin, DictMixin, SaveMixin, StatusMixin):
    """
    Stormpath Phone resource.

    More info in documentation:
    https://docs.stormpath.com/python/product-guide/latest/auth_n.html#using-multi-factor-authentication
    """
    writable_attrs = ('number', 'status', 'verification_status')
    STATUS_VERIFIED = 'VERIFIED'
    STATUS_UNVERIFIED = 'UNVERIFIED'

    @staticmethod
    def get_resource_attributes():
        from .account import Account
        return {'account': Account}

    def is_verified(self):
        return self.verification_status == self.STATUS_VERIFIED


class PhoneList(CollectionResource):
    """Phone resource list."""
    resource_class = Phone

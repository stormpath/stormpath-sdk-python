"""Stormpath Factors resource mappings."""

from .base import CollectionResource, DeleteMixin, DictMixin, Resource, SaveMixin


class Challenge(Resource, DeleteMixin, DictMixin, SaveMixin):
    """
    Stormpath Challenge resource.

    More info in documentation:
    https://docs.stormpath.com/python/product-guide/latest/auth_n.html#using-multi-factor-authentication
    """
    writable_attrs = ('message', 'code')
    STATUS_SUCCESS = 'SUCCESS'
    STATUS_CREATED = 'CREATED'
    STATUS_WAITING = 'WAITING'

    @staticmethod
    def get_resource_attributes():
        from .account import Account
        from .factor import Factor

        return {
            'account': Account,
            'factor': Factor,
        }

    def submit(self, code):
        """
        This method will submit a challenge and attempt to activate the
        associated account (if the code is valid).

        :param str code: Account activation code.
        """
        self.code = code
        self.save()
        self.refresh()

        return self

    def is_successful(self):
        return self.status == self.STATUS_SUCCESS

    def is_created(self):
        return self.status == self.STATUS_CREATED

    def is_waiting(self):
        return self.STATUS_WAITING in self.status


class ChallengeList(CollectionResource):
    """Challenge resource list."""
    resource_class = Challenge

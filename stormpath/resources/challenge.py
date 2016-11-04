"""Stormpath Factors resource mappings."""

from .base import (
    CollectionResource,
    DeleteMixin,
    DictMixin,
    Resource,
    SaveMixin,
    StatusMixin,
)


class Challenge(Resource, DeleteMixin, DictMixin, SaveMixin, StatusMixin):
    """
    Stormpath Challenge resource.
    """

    writable_attrs = ('message', )

    @staticmethod
    def get_resource_attributes():
        from .account import Account
        from .factor import Factor

        return {
            'account': Account,
            'factor': Factor,
        }

    def submit_challenge(self, code):
        """
        This method will submit a challenge and attempt to activate the
        associated account (if the code is valid).

        :param str code: Account activation code.
        """
        data = {'code': code}
        self._store.update_resource(self.href, data)
        self.refresh()

        return self


class ChallengeList(CollectionResource):
    """Challenge resource list."""
    resource_class = Challenge

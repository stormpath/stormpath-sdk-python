"""Stormpath Factors resource mappings."""

from .base import (
    CollectionResource,
    DeleteMixin,
    DictMixin,
    Resource,
    SaveMixin,
    StatusMixin,
)
from .phone import Phone


class Factor(Resource, DeleteMixin):

    writable_attrs = ('type', 'phone', 'challenge')

    @staticmethod
    def get_resource_attributes():
        from .account import Account
        from .challenge import Challenge, ChallengeList

        return {
            'account': Account,
            'challenges': ChallengeList,
            'most_recent_challenge': Challenge,
            'phone': Phone
        }

    def challenge_factor(self, message):
        """
        This method will challenge a factor and by sending the activation
        code.

        :param str message: SMS message template. Message must contain '%s'
               format specifier that serves as the activation code placeholder.
        """
        data = {'message': message}
        self._store.update_resource(self.href + '/challenges', data)
        self.refresh()

        return self.most_recent_challenge


class FactorList(CollectionResource):
    """Factor resource list."""
    resource_class = Factor

    def create(self, properties, challenge=True, expand=None, **params):
        """
        """
        if not challenge:
            properties.pop('challenge', None)

        return super(FactorList, self).create(
            properties, challenge=challenge, expand=expand, **params)

"""Stormpath Factors resource mappings."""

from .base import (
    CollectionResource,
    DeleteMixin,
    DictMixin,
    Resource,
    SaveMixin,
    StatusMixin,
)


class Challenge(Resource):
    @staticmethod
    def get_resource_attributes():
        from .account import Account
        from .factor import Factor

        return {
            'account': Account,
            'factor': Factor,
        }


class ChallengeList(CollectionResource):
    """Challenge resource list."""
    resource_class = Challenge

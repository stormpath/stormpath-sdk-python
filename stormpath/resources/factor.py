"""Stormpath Factors resource mappings."""

from .base import (
    CollectionResource,
    DeleteMixin,
    DictMixin,
    Resource,
    SaveMixin,
    StatusMixin,
)


class Factor(Resource):

    @staticmethod
    def get_resource_attributes():
        from .account import Account
        from .challenge import Challenge, ChallengeList
        from .phone import Phone

        return {
            'account': Account,
            'challenges': ChallengeList,
            'most_recent_challenge': Challenge,
            'phone': Phone
        }


class FactorList(CollectionResource):
    """Factor resource list."""
    resource_class = Factor

    """
    def create_factor(self, properties=None, expand=None, **params):
        # FIXME: implement option that will challenge factor upon creating it
        #result = self.create(properties, expand=expand)

        create_path = self.href

        created = self.resource_class(
            self._client,
            properties=self._store.create_resource(
                create_path,
                data,
                params=params
            )
        )

        created = result

        return result
    """

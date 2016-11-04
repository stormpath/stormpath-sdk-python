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


class Factor(Resource, DeleteMixin, DictMixin, SaveMixin, StatusMixin):
    """
    Stormpath Factor resource.
    """

    writable_attrs = ('type', 'phone', 'challenge')
    default_message = 'Your verification code is ${code}'

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

    def challenge_factor(self, message=default_message, code=None):
        """
        This method will challenge a factor and by sending the activation
        code.

        :param str message: SMS message template. Message must contain '%s'
               format specifier that serves as the activation code placeholder.
        :param str code: Activation code that should be passed on challenge
               creation if factor type is 'google-authenticator'.
        """
        data = {'message': message}
        if self.type == 'google-authenticator':
            if code is None:
                raise ValueError(
                    'When challenging a google-authenticator factor, ' +
                    'activation code must be provided.')
            data['code'] = code
        self._store.update_resource(self.href + '/challenges', data)
        self.refresh()

        return self.most_recent_challenge


class FactorList(CollectionResource):
    """Factor resource list."""
    resource_class = Factor

    def create(self, properties, challenge=True, expand=None, **params):
        """
        This methods will check for the challenge argument, set the proper
        message (custom or default), and call the CollectionResource create
        method.

        :param bool challenge: Determines if a challenge is created on factor
               creation.
        """
        if not challenge:
            # If we set url query string challenge to false, make sure that
            # challenge is also absent from the body, otherwise a challenge
            # will be created.
            properties.pop('challenge', None)
        elif challenge and 'message' not in properties.get('challenge', {}):
            # Set default message if one is not specified.
            properties['challenge'] = {
                'message': self.resource_class.default_message}

        return super(FactorList, self).create(
            properties, challenge=challenge, expand=expand, **params)

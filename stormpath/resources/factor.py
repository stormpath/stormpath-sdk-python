"""Stormpath Factors resource mappings."""

from .base import CollectionResource, DeleteMixin, DictMixin, Resource, SaveMixin, StatusMixin
from .phone import Phone


class Factor(Resource, DeleteMixin, DictMixin, SaveMixin, StatusMixin):
    """
    Stormpath Factor resource.

    More info in documentation:
    https://docs.stormpath.com/python/product-guide/latest/auth_n.html#using-multi-factor-authentication
    """
    writable_attrs = ('type', 'phone', 'challenge', 'status', 'issuer', 'account_name')
    STATUS_VERIFIED = 'VERIFIED'
    STATUS_UNVERIFIED = 'UNVERIFIED'
    TYPE_SMS = 'SMS'
    TYPE_GOOGLE = 'google-authenticator'

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

    def is_verified(self):
        return self.verification_status == self.STATUS_VERIFIED

    def is_sms(self):
        return self.type == 'SMS'

    def challenge_factor(self, message=None, code=None):
        """
        This method will challenge a factor and by sending the activation
        code.

        :param str message: SMS message template. Message must contain '%s'
               format specifier that serves as the activation code placeholder.
        :param str code: Activation code that should be passed on challenge
               creation if factor type is 'google-authenticator'.
        """
        if self.is_sms():
            properties = {'message': message}
        else:
            if code is None:
                raise ValueError('When challenging a google-authenticator factor, activation code must be provided.')

            properties = {'code': code}

        challenge = self.challenges.create(properties=properties)
        self.refresh()

        return challenge


class FactorList(CollectionResource):
    """Factor resource list."""
    resource_class = Factor

    def create(self, properties, expand=None, **params):
        """
        This method will check for the challenge argument, set the proper
        message (custom or default), and call the CollectionResource create
        method.

        :param bool challenge: Determines if a challenge is created on factor
               creation.
        """
        if (
            properties.get('type') == 'SMS' and
            params.get('challenge') is False and
            properties.get('challenge')
        ):
            # If the url query string challenge is false, make sure that
            # challenge is also absent from the body, otherwise a
            # challenge will be created.
            raise ValueError('If challenge is set to False, it must also be absent from properties.')

        return super(FactorList, self).create(properties, expand=expand, **params)

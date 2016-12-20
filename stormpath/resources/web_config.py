"""Stormpath WebConfig resource mappings."""

from .base import (
    StatusMixin,
    DictMixin,
    Resource,
    FixedAttrsDict,
    SaveMixin
)


class EnableAttrDict(FixedAttrsDict):

    writable_attrs = (
        'enabled'
    )


class MeExpansionDict(FixedAttrsDict):

    writable_attrs = (
        'api_keys',
        'applications',
        'custom_data',
        'directory',
        'group_memberships',
        'groups',
        'provider_data',
        'tenant'
    )


class MeDict(FixedAttrsDict):

    writable_attrs = (
        'enabled',
        'expand'
    )

    @staticmethod
    def get_dict_attributes():

        return {
            'expand': MeExpansionDict
        }


class WebConfig(Resource, StatusMixin, SaveMixin, DictMixin):

    writable_attrs = (
        'status',
        'dns_label',
        'oauth2',
        'register',
        'verify_email',
        'login',
        'forgot_password',
        'change_password',
        'me'
    )

    @staticmethod
    def get_resource_attributes():

        return {
            'oauth2': EnableAttrDict,
            'register': EnableAttrDict,
            'verify_email': EnableAttrDict,
            'login': EnableAttrDict,
            'forgot_password': EnableAttrDict,
            'change_password': EnableAttrDict,
            'me': MeDict
        }

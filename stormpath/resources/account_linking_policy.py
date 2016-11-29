"""Stormpath AccountLinkingPolicy resource mappings."""


from .base import (
    DictMixin,
    Resource,
    SaveMixin,
    StatusMixin
)


class AccountLinkingPolicy(Resource, DictMixin, SaveMixin, StatusMixin):
    """Stormpath AccountLinkingPolicy resource.

    More info in documentation:
    https://docs.stormpath.com/rest/product-guide/latest/reference.html#account-linking-policy
    """

    AUTOMATIC_PROVISIONING_ENABLED = 'ENABLED'
    AUTOMATIC_PROVISIONING_DISABLED = 'DISABLED'

    MATCHING_PROPERTY_EMAIL = 'email'
    MATCHING_PROPERTY_NULL = None

    writable_attrs = (
        'status',
        'automatic_provisioning',
        'matching_property'
    )

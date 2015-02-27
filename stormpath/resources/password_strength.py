"""Stormpath PasswordStrength resource mappings."""


from .base import (
    DictMixin,
    Resource,
    SaveMixin,
)


class PasswordStrength(Resource, DictMixin, SaveMixin):
    """Stormpath PasswordStrength resource.

    More info in documentation:
    http://docs.stormpath.com/rest/product-guide/#directory-password-policy
    (Password Strength Policy for Directory's Accounts section)
    """

    writable_attrs = (
        'max_length',
        'min_diacritic',
        'min_length',
        'min_lower_case',
        'min_numeric',
        'min_symbol',
        'min_upper_case',
    )

"""Stormpath PasswordStrength resource mappings."""


import unicodedata

from .base import (
    DictMixin,
    Resource,
    SaveMixin,
)


def _is_diacritic(char):
    try:
        name = unicodedata.name(char)
    except ValueError:
        name = ''

    return (
        unicodedata.category(char) == 'Mn' or unicodedata.combining(char) or
        ' WITH ' in name)

def _get_ord(char):
    try:
        return ord(char)
    except TypeError:
        # Python 3 does not need ord()
        return char


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

    def validate_password(self, password):
        if len(password) > self.max_length:
            raise ValueError('Password exceeded the maximum length.')

        if len(password) < self.min_length:
            raise ValueError('Password minimum length not satisfied.')

        num_of_lower_case = sum(1 for c in password if c.islower())

        if num_of_lower_case < self.min_lower_case:
            raise ValueError(
                'Password requires at least %d lowercase characters.' %
                self.min_lower_case)

        num_of_numeric = sum(1 for c in password if c.isdigit())

        if num_of_numeric < self.min_numeric:
            raise ValueError(
                'Password requires at least %d numeric characters.' %
                self.min_numeric)

        num_of_symbol = sum(
            1 for c in password if (
                _get_ord(c) in range(1, 126) and not c.isdigit()
                and not c.isalpha()))

        if num_of_symbol < self.min_symbol:
            raise ValueError(
                'Password requires at least %d symbol characters.' %
                self.min_symbol)

        num_of_upper_case = sum(1 for c in password if c.isupper())

        if num_of_upper_case < self.min_upper_case:
            raise ValueError(
                'Password requires at least %d uppercase characters.' %
                self.min_upper_case)

        num_of_diacritic = sum(1 for c in password if _is_diacritic(c))

        if num_of_diacritic < self.min_diacritic:
            raise ValueError(
                'Password requires at least %d diacritic characters.' %
                self.min_diacritic)

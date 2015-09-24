# -*- coding: utf-8 -*-

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

    NUMERIC_DIGIT_MIN = u'\u0030'
    NUMERIC_DIGIT_MAX = u'\u0039'

    UPPER_CASE_LETTER_MIN = u'\u0041'
    UPPER_CASE_LETTER_MAX = u'\u005A'

    LOWER_CASE_LETTER_MIN = u'\u0061'
    LOWER_CASE_LETTER_MAX = u'\u007A'

    SYMBOL_CHARS = (
        u'\u0020',  #
        u'\u0021',  # !
        u'\u0022',  # "
        u'\u0023',  # #
        u'\u0024',  # $
        u'\u0025',  # %
        u'\u0026',  # &
        u'\u0027',  # '
        u'\u0028',  # (
        u'\u0029',  # )
        u'\u002A',  # *
        u'\u002B',  # +
        u'\u002C',  # ,
        u'\u002D',  # -
        u'\u002E',  # .
        u'\u002F',  # /
        u'\u003A',  # :
        u'\u003B',  # ;
        u'\u003C',  # <
        u'\u003D',  # =
        u'\u003E',  # >
        u'\u003F',  # ?
        u'\u0040',  # @
        u'\u005B',  # [
        u'\u005C',  # \
        u'\u005D',  # ]
        u'\u005E',  # ^
        u'\u005F',  # _
        u'\u0060',  # `
        u'\u007B',  # {
        u'\u007D',  # }
        u'\u007E',  # ~
        u'\u007C',  # |
        u'\u00A1',  # ¡
        u'\u00A6',  # ¦
        u'\u00A7',  # §
        u'\u00A9',  # ©
        u'\u00AB',  # «
        u'\u00AC',  # ¬
        u'\u00AE',  # ®
        u'\u00B1',  # ±
        u'\u00B5',  # µ
        u'\u00B6',  # ¶
        u'\u00B7',  # ·
        u'\u00BB',  # »
        u'\u00BD',  # ½
        u'\u00BF',  # ¿
        u'\u00D7',  # ×
        u'\u00F7')  # ÷

    DIACRITIC_CHARS = (
        u'\u00C0',  # À
        u'\u00C1',  # Á
        u'\u00C2',  # Â
        u'\u00C3',  # Ã
        u'\u00C4',  # Ä
        u'\u00C5',  # Å
        u'\u00C6',  # Æ
        u'\u00C7',  # Ç
        u'\u00C8',  # È
        u'\u00C9',  # É
        u'\u00CA',  # Ê
        u'\u00CB',  # Ë
        u'\u00CC',  # Ì
        u'\u00CD',  # Í
        u'\u00CE',  # Î
        u'\u00CF',  # Ï
        u'\u00D0',  # Ð
        u'\u00D1',  # Ñ
        u'\u00D2',  # Ò
        u'\u00D3',  # Ó
        u'\u00D4',  # Ô
        u'\u00D5',  # Õ
        u'\u00D6',  # Ö
        u'\u00D8',  # Ø
        u'\u00D9',  # Ù
        u'\u00DA',  # Ú
        u'\u00DB',  # Û
        u'\u00DC',  # Ü
        u'\u00DD',  # Ý
        u'\u00DE',  # Þ
        u'\u00DF',  # ß
        u'\u00E0',  # à
        u'\u00E1',  # á
        u'\u00E2',  # â
        u'\u00E3',  # ã
        u'\u00E4',  # ä
        u'\u00E5',  # å
        u'\u00E6',  # æ
        u'\u00E7',  # ç
        u'\u00E8',  # è
        u'\u00E9',  # é
        u'\u00EA',  # ê
        u'\u00EB',  # ë
        u'\u00EC',  # ì
        u'\u00ED',  # í
        u'\u00EE',  # î
        u'\u00EF',  # ï
        u'\u00F0',  # ð
        u'\u00F1',  # ñ
        u'\u00F2',  # ò
        u'\u00F3',  # ó
        u'\u00F4',  # ô
        u'\u00F5',  # õ
        u'\u00F6',  # ö
        u'\u00F8',  # ø
        u'\u00F9',  # ù
        u'\u00FA',  # ú
        u'\u00FB',  # û
        u'\u00FC',  # ü
        u'\u00FD',  # ý
        u'\u00FE',  # þ
        u'\u00FF')  # ÿ

    def validate_password(self, password):
        if len(password) > self.max_length:
            raise ValueError('Password exceeded the maximum length.')

        if len(password) < self.min_length:
            raise ValueError('Password minimum length not satisfied.')

        num_of_lower_case = sum(1 for c in password if (
            self.LOWER_CASE_LETTER_MIN <= c <= self.LOWER_CASE_LETTER_MAX))

        if num_of_lower_case < self.min_lower_case:
            raise ValueError(
                'Password requires at least %d lowercase characters.' %
                self.min_lower_case)

        num_of_numeric = sum(
            1 for c in password if (
                self.NUMERIC_DIGIT_MIN <= c <= self.NUMERIC_DIGIT_MAX))

        if num_of_numeric < self.min_numeric:
            raise ValueError(
                'Password requires at least %d numeric characters.' %
                self.min_numeric)

        num_of_symbol = sum(
            1 for c in password if c in self.SYMBOL_CHARS)

        if num_of_symbol < self.min_symbol:
            raise ValueError(
                'Password requires at least %d symbol characters.' %
                self.min_symbol)

        num_of_upper_case = sum(1 for c in password if (
            self.UPPER_CASE_LETTER_MIN <= c <= self.UPPER_CASE_LETTER_MAX))

        if num_of_upper_case < self.min_upper_case:
            raise ValueError(
                'Password requires at least %d uppercase characters.' %
                self.min_upper_case)

        num_of_diacritic = sum(
            1 for c in password if c in self.DIACRITIC_CHARS)

        if num_of_diacritic < self.min_diacritic:
            raise ValueError(
                'Password requires at least %d diacritic characters.' %
                self.min_diacritic)

""""
Integration tests for various pieces involved in external provider support.
"""

from unittest import TestCase, main
from stormpath.resources.email_template import DefaultModelEmailTemplate
from stormpath.resources.password_policy import PasswordPolicy
from stormpath.resources.password_strength import PasswordStrength

try:
    from mock import MagicMock
except ImportError:
    from unittest.mock import MagicMock

from stormpath.resources.directory import DirectoryList


class TestPasswordPolicy(TestCase):

    def test_creating_directory_with_defined_password_policy(self):
        ds = MagicMock()
        ds.create_resource.return_value = {}

        dl = DirectoryList(
            client=MagicMock(data_store=ds, BASE_URL='http://example.com'),
            href='directories')

        dl.create({
            'name': 'Foo',
            'description': 'Desc',
            'password_policy': {
                'reset_email_status':
                    PasswordPolicy.RESET_EMAIL_STATUS_ENABLED,
                'reset_success_email_status':
                    PasswordPolicy.RESET_EMAIL_STATUS_ENABLED,
                'reset_token_ttl': 32
                }
        })

        ds.create_resource.assert_called_once_with(
            'http://example.com/directories', {
                'passwordPolicy': {
                    'resetSuccessEmailStatus': 'ENABLED',
                    'resetEmailStatus': 'ENABLED',
                    'resetTokenTtl': 32
                },
                'description': 'Desc',
                'name': 'Foo',
            }, params={})

    def test_modifying_password_policy(self):
        ds = MagicMock()
        ds.update_resource.return_value = {}

        pp = PasswordPolicy(
            client=MagicMock(data_store=ds, BASE_URL='http://example.com'),
            href='password-policy')

        pp._set_properties({'reset_token_ttl': 100})
        pp.save()

        ds.update_resource.assert_called_once_with(
            'password-policy', {'resetTokenTtl': 100, })

    def test_modifying_password_strength(self):
        ds = MagicMock()
        ds.update_resource.return_value = {}

        ps = PasswordStrength(
            client=MagicMock(data_store=ds, BASE_URL='http://example.com'),
            href='strength')

        ps._set_properties({'min_length': 15})
        ps.save()

        ds.update_resource.assert_called_once_with(
            'strength', {'minLength': 15, })

    def test_reset_email_get_link_base_url(self):
        ds = MagicMock()
        ds.get_resource.return_value = {
            'defaultModel': {'linkBaseUrl': 'some-link.com'}
        }

        ret = DefaultModelEmailTemplate(
            client=MagicMock(data_store=ds, BASE_URL='http://example.com'),
            href='email-template')

        self.assertTrue(ret.get_link_base_url(), 'some-link.com')

    def test_reset_email_set_link_base_url(self):
        ds = MagicMock()
        ds.get_resource.return_value = {
            'defaultModel': {
                'linkBaseUrl': 'https://api.stormpath.com/passwordReset'
            }
        }
        ds.update_resource.return_value = {}

        ret = DefaultModelEmailTemplate(
            client=MagicMock(data_store=ds, BASE_URL='http://example.com'),
            href='email-template')

        ret.set_link_base_url('some-link.com')
        self.assertTrue(ret.default_model, {'linkBaseUrl': 'some-link.com'})


class TestPasswordStrength(TestCase):
    def setUp(self):
        default_properties = {
            'max_length': 100,
            'min_length': 8,
            'min_lower_case': 1,
            'min_numeric': 1,
            'min_symbol': 0,
            'min_upper_case': 1,
            'min_diacritic': 0
        }
        self.password_strength = PasswordStrength(
            client=MagicMock(),
            properties=default_properties)

    def test_validate_password_max_length(self):
        self.password_strength.max_length = 10
        invalid_password = u'i-am-longer-then-10'

        with self.assertRaises(ValueError) as error:
            self.password_strength.validate_password(invalid_password)
        self.assertEqual(
            'Password exceeded the maximum length.', str(error.exception))

        valid_password = u'!-Am-Sma11'
        self.password_strength.validate_password(valid_password)

    def test_validate_password_min_length(self):
        self.password_strength.min_length = 25
        invalid_password = u'shorter-then-25'

        with self.assertRaises(ValueError) as error:
            self.password_strength.validate_password(invalid_password)
        self.assertEqual(
            'Password minimum length not satisfied.', str(error.exception))

        valid_password = u'!-Am-S000000-L000000000NG'
        self.password_strength.validate_password(valid_password)

    def test_validate_password_min_lower_case(self):
        self.password_strength.min_lower_case = 5
        invalid_password = u'JUST-1-LOWER-CASe'

        with self.assertRaises(ValueError) as error:
            self.password_strength.validate_password(invalid_password)
        self.assertEqual(
            'Password requires at least 5 lowercase characters.',
            str(error.exception))

        valid_password = u'en0ugh-lowerCASE'
        self.password_strength.validate_password(valid_password)

    def test_validate_password_min_numeric(self):
        self.password_strength.min_numeric = 5
        invalid_password = u'JUST-1-numeric'

        with self.assertRaises(ValueError) as error:
            self.password_strength.validate_password(invalid_password)
        self.assertEqual(
            'Password requires at least 5 numeric characters.',
            str(error.exception))

        valid_password = u'1-am-S000-nUm3r1c'
        self.password_strength.validate_password(valid_password)

    def test_validate_password_min_symbol(self):
        self.password_strength.min_symbol = 5
        invalid_password = u'JUST-2-symbols'

        with self.assertRaises(ValueError) as error:
            self.password_strength.validate_password(invalid_password)
        self.assertEqual(
            'Password requires at least 5 symbol characters.',
            str(error.exception))

        valid_password = u'@!NOW-6-symbols!@'
        self.password_strength.validate_password(valid_password)

        with self.assertRaises(ValueError) as error:
            invalid_password = u'\u2600\u2600-\u26006-SymbS\u2600-\u2600\u2600'
            self.password_strength.validate_password(invalid_password)
        self.assertEqual(
            'Password requires at least 5 symbol characters.',
            str(error.exception))

        with self.assertRaises(ValueError) as error:
            invalid_password = u'\u0082\u0082-\u00826-SymbS\u0082-\u0082\u0082'
            self.password_strength.validate_password(invalid_password)
        self.assertEqual(
            'Password requires at least 5 symbol characters.',
            str(error.exception))

    def test_validate_password_min_upper_case(self):
        self.password_strength.min_upper_case = 5
        invalid_password = u'JUST-4-upper-cases'

        with self.assertRaises(ValueError) as error:
            self.password_strength.validate_password(invalid_password)
        self.assertEqual(
            'Password requires at least 5 uppercase characters.',
            str(error.exception))

        valid_password = u'NOW-7-UPPER-cases'
        self.password_strength.validate_password(valid_password)

    def test_validate_password_min_diacritic(self):
        self.password_strength.min_diacritic = 2
        invalid_password = u'JUST-1-diacritic\u00c0'

        with self.assertRaises(ValueError) as error:
            self.password_strength.validate_password(invalid_password)
        self.assertEqual(
            'Password requires at least 2 diacritic characters.',
            str(error.exception))

        valid_password = u'\u00c0-2-Diacritics-\u00c0'
        self.password_strength.validate_password(valid_password)

        # \u20d0 is not a diacritic in Stormpath
        invalid_password = u'\u20d0-2-Diacritics-\u20d0'
        with self.assertRaises(ValueError) as error:
            self.password_strength.validate_password(invalid_password)
        self.assertEqual(
            'Password requires at least 2 diacritic characters.',
            str(error.exception))

        # \u2600 is not a diacritic in Stormpath
        with self.assertRaises(ValueError) as error:
            self.password_strength.validate_password(invalid_password)
        self.assertEqual(
            'Password requires at least 2 diacritic characters.',
            str(error.exception))


if __name__ == '__main__':
    main()

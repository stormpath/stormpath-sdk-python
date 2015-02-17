""""
Integration tests for various pieces involved in external provider support.
"""

from unittest import TestCase, main
from stormpath.resources.email_template import ResetEmailTemplate
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

        ret = ResetEmailTemplate(
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

        ret = ResetEmailTemplate(
            client=MagicMock(data_store=ds, BASE_URL='http://example.com'),
            href='email-template')

        ret.set_link_base_url('some-link.com')
        self.assertTrue(ret.default_model, {'linkBaseUrl': 'some-link.com'})


if __name__ == '__main__':
    main()

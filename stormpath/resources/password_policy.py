"""Stormpath PasswordPolicy resource mappings."""


from .base import (
    DictMixin,
    Resource,
    SaveMixin,
)


class PasswordPolicy(Resource, DictMixin, SaveMixin):
    """Stormpath PasswordPolicy resource.

    More info in documentation:
    http://docs.stormpath.com/rest/product-guide/#directory-password-policy
    """

    RESET_EMAIL_STATUS_ENABLED = 'ENABLED'
    RESET_EMAIL_STATUS_DISABLED = 'DISABLED'

    writable_attrs = (
        'reset_email_status',
        'reset_success_email_status',
        'reset_token_ttl',
    )

    @staticmethod
    def get_resource_attributes():
        from .email_template import EmailTemplateList, DefaultModelEmailTemplateList
        from .password_strength import PasswordStrength

        return {
            'reset_email_templates': DefaultModelEmailTemplateList,
            'reset_success_email_templates': EmailTemplateList,
            'strength': PasswordStrength,
        }

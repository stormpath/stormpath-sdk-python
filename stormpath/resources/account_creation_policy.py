"""Stormpath AccountCreationPolicy resource mappings."""


from .base import (
    DictMixin,
    Resource,
    SaveMixin,
)


class AccountCreationPolicy(Resource, DictMixin, SaveMixin):
    """Stormpath AccountCreationPolicy resource.

    More info in documentation:
    http://docs.stormpath.com/rest/product-guide/#directory-account-creation-policy
    """

    EMAIL_STATUS_ENABLED = 'ENABLED'
    EMAIL_STATUS_DISABLED = 'DISABLED'

    writable_attrs = (
        'verification_email_status',
        'verification_success_email_status',
        'welcome_email_status',
    )

    @staticmethod
    def get_resource_attributes():
        from .email_template import (
            EmailTemplateList,
            DefaultModelEmailTemplateList
        )

        return {
            'verification_email_templates': DefaultModelEmailTemplateList,
            'verification_success_email_templates': EmailTemplateList,
            'welcome_email_templates': EmailTemplateList,
        }

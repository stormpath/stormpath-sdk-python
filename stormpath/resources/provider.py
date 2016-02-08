"""Stormpath Provider resource mappings."""


from .base import (
    DeleteMixin,
    DictMixin,
    Resource,
    SaveMixin,
)


class Provider(Resource, DeleteMixin, DictMixin, SaveMixin):
    """Stormpath Provider resource.

    More info in documentation:
    http://docs.stormpath.com/python/product-guide/#integrating-with-google
    """

    GOOGLE = 'google'
    FACEBOOK = 'facebook'
    GITHUB = 'github'
    LINKEDIN = 'linkedin'
    STORMPATH = 'stormpath'
    SAML = 'saml'

    SIGNING_ALGORITHM_RSA_SHA_1 = 'RSA-SHA1'
    SIGNING_ALGORITHM_RSA_SHA_256 = 'RSA-SHA256'

    writable_attrs = (
        'agent',
        'attribute_statement_mapping_rules',
        'client_id',
        'client_secret',
        'encoded_x509_signing_cert',
        'redirect_uri',
        'request_signature_algorithm',
        'provider_id',
        'sso_login_url',
        'sso_logout_url',
    )

    @staticmethod
    def get_resource_attributes():
        from .agent import Agent
        from .attribute_statement_mapping_rule import AttributeStatementMappingRules
        from .saml_service_provider_metadata import SamlServiceProviderMetadata

        return {
            'agent': Agent,
            'attribute_statement_mapping_rules': AttributeStatementMappingRules,
            'service_provider_metadata': SamlServiceProviderMetadata
        }

    def save(self):
        if self.provider_id == self.STORMPATH:
            return

        super(Provider, self).save()

"""Stormpath SAML service provider."""


from .base import (
    DictMixin,
    Resource,
    StatusMixin,
    SaveMixin
)


class SamlIdentityProvider(Resource, DictMixin, StatusMixin, SaveMixin):
    """
    SamlIdentityProvider resource.

    """

    writable_attrs = (
        'status'
    )

    @staticmethod
    def get_resource_attributes():
        from .sso_login_endpoint import SsoLoginEndpoint
        from .saml_signing_cert import X509SigningCert
        from .saml_identity_provider_metadata import SamlIdentityProviderMetadata
        from .attribute_statement_mapping_rule import AttributeStatementMappingRules
        from .registered_saml_service_providers import RegisteredSamlServiceProviders
        from .saml_service_provider_registrations import SamlServiceProviderRegistrations

        return {
            'sso_login_endpoint': SsoLoginEndpoint,
            'x509_signing_cert': X509SigningCert,
            'saml_identity_provider_metadata': SamlIdentityProviderMetadata,
            'attribute_statement_mapping_rules': AttributeStatementMappingRules,
            'registered_saml_service_providers': RegisteredSamlServiceProviders,
            'saml_service_provider_registrations': SamlServiceProviderRegistrations
        }

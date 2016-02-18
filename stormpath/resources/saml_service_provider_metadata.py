"""Stormpath SAML service provider metadata."""


from .base import (
    DictMixin,
    Resource,
)


class SamlServiceProviderMetadata(Resource, DictMixin):
    """SamlServiceProviderMetadata resource.
    """
    @staticmethod
    def get_resource_attributes():
        from .assertion_consumer_service_post_endpoint import (
            AssertionConsumerServicePostEndpoint
        )

        return {
            'assertion_consumer_service_post_endpoint':
                AssertionConsumerServicePostEndpoint
        }

"""Stormpath SAML service provider."""


from .base import (
    DictMixin,
    Resource,
)


class SamlServiceProvider(Resource, DictMixin):
    """SamlServiceProvider resource.
    """
    @staticmethod
    def get_resource_attributes():
        from .sso_initiation_endpoint import SsoInitiationEndpoint

        return {
            'sso_initiation_endpoint': SsoInitiationEndpoint
        }

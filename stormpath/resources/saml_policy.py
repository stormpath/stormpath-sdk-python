"""Stormpath SAML policy."""


from .base import (
    DictMixin,
    Resource,
)


class SamlPolicy(Resource, DictMixin):
    """SamlPolicy resource.
    """
    @staticmethod
    def get_resource_attributes():
        from .saml_service_provider import SamlServiceProvider

        return {
            'service_provider': SamlServiceProvider
        }

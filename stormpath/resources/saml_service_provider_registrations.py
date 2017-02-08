"""Stormpath SAML Service Provider Registrations endpoint
   on SAML Identity Provider."""


from .base import (
    DictMixin,
    Resource,
    CollectionResource
)


class SamlServiceProviderRegistration(Resource, DictMixin):
    """SamlServiceProviderRegistration resource.
    """
    pass


class SamlServiceProviderRegistrations(CollectionResource):
    """SamlServiceProviderRegistrations collection resource.
    """
    resource_class = SamlServiceProviderRegistration

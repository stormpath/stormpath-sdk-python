"""Stormpath Registered SAML Service Providers endpoint
   on SAML Identity Provider."""


from .base import (
    DictMixin,
    Resource,
    CollectionResource
)


class RegisteredSamlServiceProvider(Resource, DictMixin):
    """RegisteredSamlServiceProvider resource.
    """


class RegisteredSamlServiceProviders(CollectionResource):
    """RegisteredSamlServiceProviders collection resource.
    """
    resource_class = RegisteredSamlServiceProvider

"""Stormpath Default relay state."""


from .base import (
    CollectionResource,
    FixedAttrsDict,
)


class DefaultRelayState(FixedAttrsDict):
    writable_attrs = (
        'callback_uri',
        'organization',
        'state',
    )


class DefaultRelayStateList(CollectionResource):
    """Stormpath DefaultRelayState list."""
    resource_class = DefaultRelayState

    def create(self, properties=None, expand=None, **params):
        if properties is None:
            properties = {}

        return super(DefaultRelayStateList, self).create(
            properties, expand, **params)

    @staticmethod
    def _sanitize_property(value):
        from stormpath.resources import Organization

        if isinstance(value, Organization):
            return {'nameKey': value.name_key}

        return CollectionResource._sanitize_property(value)

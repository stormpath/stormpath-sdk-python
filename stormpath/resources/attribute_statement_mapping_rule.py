"""Stormpath Attribute statement mapping rule."""


from .base import (
    SaveMixin,
    Resource,
    FixedAttrsDict,
    ListOnResource
)


class AttributeStatementMappingRule(FixedAttrsDict):
    """Stormpath Attribute statement mapping rule.
    """
    writable_attrs = ('name', 'name_format', 'account_attributes')

    def __init__(self, **kwargs):
        self._set_properties(kwargs)


class AttributeStatementMappingRules(Resource, SaveMixin):
    """AttributeStatementMappingRules resource.
    """
    writable_attrs = ('items', )

    @staticmethod
    def get_resource_attributes():
        return {
            'items': ListOnResource,
        }

    def _wrap_resource_attr(self, cls, value):
        if isinstance(value, list) and cls == ListOnResource:
            return cls(
                self._client, properties=value,
                type=AttributeStatementMappingRule)

        return super(AttributeStatementMappingRules, self)._wrap_resource_attr(
            cls, value)

    @staticmethod
    def _sanitize_property(value):
        if isinstance(value, ListOnResource):
            return value._get_properties()

        return super(AttributeStatementMappingRules, self)._sanitize_property(
            value)

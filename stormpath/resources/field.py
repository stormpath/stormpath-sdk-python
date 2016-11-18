"""Stormpath Field resource mappings."""


from .base import CollectionResource, DictMixin, Resource, SaveMixin


class Field(Resource, DictMixin, SaveMixin):
    """Field resource.

    More info in documentation:
    https://docs.stormpath.com/rest/product-guide/latest/accnt_mgmt.html#account-schema
    """
    writable_attrs = ('required',)

    @staticmethod
    def get_resource_attributes():
        from .account_schema import AccountSchema

        return {'account_schema': AccountSchema}


class FieldList(CollectionResource):
    """Field resource list."""
    resource_class = Field

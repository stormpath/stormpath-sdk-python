# -*- coding: utf-8 -*-

"""Stormpath AccountSchema resource mappings."""


from .base import DictMixin, Resource, SaveMixin


class AccountSchema(Resource, DictMixin, SaveMixin):
    """Stormpath AccountSchema resource.

    More info in documentation:
    https://docs.stormpath.com/rest/product-guide/latest/reference.html#account-schema
    """

    @staticmethod
    def get_resource_attributes():
        from .directory import Directory
        from .field import Field

        return {
            'directory': Directory,
            'field': Field,
        }

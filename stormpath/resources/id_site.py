"""Stormpath IDSite resource mappings."""


from .base import (
    CollectionResource,
    DictMixin,
    Resource,
    SaveMixin,
)


class IDSite(Resource, DictMixin, SaveMixin):
    """Stormpath IDSite resource.

    More info in documentation:
    https://docs.stormpath.com/rest/product-guide/latest/reference.html#ref-id-site
    """
    writable_attrs = (
        'domain_name',
        'tls_public_cert',
        'tls_private_key',
        'git_repo_url',
        'git_branch',
        'authorized_origin_uris',
        'authorized_redirect_uris',
        'logo_url',
        'session_tti',
        'session_ttl',
        'session_cookie_persistent',
    )

    @staticmethod
    def get_resource_attributes():
        from .tenant import Tenant
        return {'tenant': Tenant}


class IDSiteList(CollectionResource):
    """IDSite resource list."""
    resource_class = IDSite

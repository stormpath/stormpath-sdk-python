"""Stormpath EmailTemplate resource mappings."""


from .base import (
    CollectionResource,
    DictMixin,
    Resource,
    SaveMixin,
)


class EmailTemplate(Resource, DictMixin, SaveMixin):
    """Stormpath EmailTemplate resource.

    More info in documentation:
    http://docs.stormpath.com/rest/product-guide/#directory-password-policy
    """

    MIME_TYPE_PLAIN_TEXT = 'text/plain'
    MIME_TYPE_HTML = 'text/html'

    writable_attrs = (
        'description',
        'from_email_address',
        'from_name',
        'html_body',
        'mime_type',
        'name',
        'subject',
        'text_body',
    )


class EmailTemplateList(CollectionResource):
    """EmailTemplate resource list."""
    resource_class = EmailTemplate


class DefaultModelEmailTemplate(EmailTemplate):
    """Stormpath DefaultModelEmailTemplate resource.

    More info in documentation:
    http://docs.stormpath.com/rest/product-guide/#directory-password-policy
    (Password Reset Workflow for Directory's Accounts section)
    """

    writable_attrs = EmailTemplate.writable_attrs + ('default_model', )

    def get_link_base_url(self):
        """
        Gets link_base_url from default_model.
        :return: Value of "linkBaseUrl" key in defaultModel dict.
        """
        return self.default_model.get('linkBaseUrl')

    def set_link_base_url(self, value):
        """
        Sets link_base_url from default_model dict..
        :param value: Value to which "linkBaseUrl" key will be set.
        """
        self.default_model['linkBaseUrl'] = value


class DefaultModelEmailTemplateList(CollectionResource):
    """DefaultModelEmailTemplate resource list."""
    resource_class = DefaultModelEmailTemplate

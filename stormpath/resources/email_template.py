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


class ResetEmailTemplate(EmailTemplate):
    """Stormpath ResetEmailTemplate resource.

    More info in documentation:
    http://docs.stormpath.com/rest/product-guide/#directory-password-policy
    (Password Reset Workflow for Directory's Accounts section)
    """

    writable_attrs = EmailTemplate.writable_attrs + ('default_model', )

    def __setattr__(self, name, value):
        if name == 'default_model':
            raise AttributeError(
                "Attribute '%s' of %s is not writable. For linkBaseUrl use "
                "get_link_base_url() and set_link_base_url()." %
                (name, self.__class__.__name__))

        super(ResetEmailTemplate, self).__setattr__(name, value)

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


class ResetEmailTemplateList(CollectionResource):
    """ResetEmailTemplate resource list."""
    resource_class = ResetEmailTemplate

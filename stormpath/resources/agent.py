"""Stormpath Provider resource mappings."""


from .base import (
    DeleteMixin,
    DictMixin,
    FixedAttrsDict,
    Resource,
    SaveMixin,
    CollectionResource, )


class AgentAccountConfig(FixedAttrsDict):
    """Stormpath Agent account config.
    """
    writable_attrs = (
        'dn_suffix', 'object_class', 'object_filter', 'email_rdn',
        'given_name_rdn', 'middle_name_rdn', 'surname_rdn', 'username_rdn',
        'password_rdn')


class AgentGroupConfig(FixedAttrsDict):
    """Stormpath Agent group config.
    """
    writable_attrs = (
        'dn_suffix', 'object_class', 'object_filter', 'name_rdn',
        'description_rdn', 'members_rdn')


class AgentConfig(FixedAttrsDict):
    """Stormpath Agent config.
    """
    writable_attrs = (
        'directory_host', 'directory_port', 'ssl_required', 'agent_user_dn',
        'agent_user_dn_password', 'base_dn', 'poll_interval', 'referral_mode',
        'ignore_referral_issues', 'account_config', 'group_config')

    @staticmethod
    def get_dict_attributes():
        return {
            'account_config': AgentAccountConfig,
            'group_config': AgentGroupConfig
        }


class AgentDownload(Resource):
    """Stormpath Agent download.
    """
    pass


class Agent(Resource, DeleteMixin, DictMixin, SaveMixin):
    """Stormpath Agent resource.
    """
    writable_attrs = ('config', )

    @staticmethod
    def get_resource_attributes():
        return {
            'config': AgentConfig,
            'download': AgentDownload
        }


class AgentList(CollectionResource):
    """Agent resource list."""
    resource_class = Agent

    def create(self, properties, expand=None, **params):
        raise ValueError(
            "Can't create new Agents, create mirror directory instead")

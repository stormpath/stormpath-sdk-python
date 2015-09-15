"""Main stormpath module."""


__author__ = 'Stormpath, Inc.'
__copyright__ = 'Copyright 2012-2015 Stormpath, Inc.'

__version_info__ = ('2', '1', '1')
__version__ = '.'.join(__version_info__)
__short_version__ = '.'.join(__version_info__)

__all__ = [
    'Cache',
    'CacheEntry',
    'CacheManager'
    'MemcachedStore',
    'MemoryStore',
    'RedisStore',
    'CacheStats',
    'Client',
    'Error',
    'IdSiteCallbackResult',
    'Account',
    'AccountList',
    'AccountCreationPolicy',
    'AccountStore',
    'AccountStoreMapping',
    'AccountStoreMappingList',
    'AgentAccountConfig',
    'AgentGroupConfig',
    'AgentConfig',
    'AgentDownload',
    'Agent',
    'AgentList',
    'ApiKey',
    'ApiKeyList',
    'Expansion',
    'Resource',
    'CollectionResource',
    'CustomData',
    'Directory',
    'DirectoryList',
    'EmailTemplate',
    'EmailTemplateList',
    'DefaultModelEmailTemplate',
    'DefaultModelEmailTemplateList',
    'Group',
    'GroupList',
    'AuthenticationResult',
    'LoginAttemptList',
    'OauthPolicy',
    'PasswordPolicy',
    'PasswordResetToken',
    'PasswordResetTokenList',
    'PasswordStrength',
    'Provider',
    'ProviderData',
    'Tenant',
    'VerificationEmail',
    'VerificationEmailList',
]


from stormpath.cache.cache import Cache
from stormpath.cache.entry import CacheEntry
from stormpath.cache.manager import CacheManager
from stormpath.cache.memcached_store import MemcachedStore
from stormpath.cache.memory_store import MemoryStore
from stormpath.cache.redis_store import RedisStore
from stormpath.cache.stats import CacheStats
from stormpath.client import Client
from stormpath.error import Error
from stormpath.id_site import IdSiteCallbackResult
from stormpath.resources.account import Account, AccountList
from stormpath.resources.account_creation_policy import AccountCreationPolicy
from stormpath.resources.account_store import AccountStore
from stormpath.resources.account_store_mapping import AccountStoreMapping, AccountStoreMappingList
from stormpath.resources.agent import AgentAccountConfig, AgentGroupConfig, AgentConfig, AgentDownload, Agent, AgentList
from stormpath.resources.api_key import ApiKey, ApiKeyList
from stormpath.resources.application import Application, ApplicationList
from stormpath.resources.base import Expansion, Resource, CollectionResource
from stormpath.resources.custom_data import CustomData
from stormpath.resources.directory import Directory, DirectoryList
from stormpath.resources.email_template import EmailTemplate, EmailTemplateList, DefaultModelEmailTemplate, DefaultModelEmailTemplateList
from stormpath.resources.group import Group, GroupList
from stormpath.resources.group_membership import GroupMembership, GroupMembershipList
from stormpath.resources.login_attempt import AuthenticationResult, LoginAttemptList
from stormpath.resources.oauth_policy import OauthPolicy
from stormpath.resources.password_policy import PasswordPolicy
from stormpath.resources.password_reset_token import PasswordResetToken, PasswordResetTokenList
from stormpath.resources.password_strength import PasswordStrength
from stormpath.resources.provider import Provider
from stormpath.resources.provider_data import ProviderData
from stormpath.resources.tenant import Tenant
from stormpath.resources.verification_email import VerificationEmail, VerificationEmailList

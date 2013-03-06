__author__ = 'ecrisostomo'

from stormpath.resource.resource import InstanceResource
from stormpath.resource.accounts import Account
from stormpath.resource.applications import Application, ApplicationList
from stormpath.resource.email_verification import EmailVerificationToken
from stormpath.resource.directories import DirectoryList

class Tenant(InstanceResource):

    NAME = "name"
    KEY = "key"
    APPLICATIONS = "applications"
    DIRECTORIES = "directories"

    @property
    def name(self):
        return self.get_property(Tenant.NAME)

    @property
    def key(self):
        return self.get_property(Tenant.KEY)

    @property
    def applications(self):
        return self._get_resource_property_(Tenant.APPLICATIONS, ApplicationList)

    @property
    def directories(self):
        return self._get_resource_property_(Tenant.DIRECTORIES, DirectoryList)

    def create_application(self, application):
        href = '/applications' #TODO enable auto discovery
        return self.data_store.create(href, application, Application)

    def verify_account_email(self, token):

        #TODO: enable auto discovery via Tenant resource (should be just /emailVerificationTokens)
        href = "/accounts/emailVerificationTokens/" + token

        token_dict = {self.HREF_PROP_NAME : href}

        ev_token = self.data_store.instantiate(EmailVerificationToken, token_dict)

        #execute a POST (should clean this up / make it more obvious)
        return self.data_store.save(ev_token, Account)


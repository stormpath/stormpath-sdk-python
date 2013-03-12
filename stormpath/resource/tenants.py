__author__ = 'ecrisostomo'

import stormpath
from stormpath.resource.resource import InstanceResource
from stormpath.resource.email_verification import EmailVerificationToken
from stormpath.util import assert_instance

class Tenant(InstanceResource):

    NAME = "name"
    KEY = "key"
    APPLICATIONS = "applications"
    DIRECTORIES = "directories"

    @property
    def name(self):
        return self.get_property(self.NAME)

    @property
    def key(self):
        return self.get_property(self.KEY)

    @property
    def applications(self):
        return self._get_resource_property_(self.APPLICATIONS, stormpath.resource.ApplicationList)

    @property
    def directories(self):
        return self._get_resource_property_(self.DIRECTORIES, stormpath.resource.DirectoryList)

    def create_application(self, application):
        assert_instance(application, stormpath.resource.Application, 'application')
        href = '/applications' #TODO enable auto discovery
        return self.data_store.create(href, application, stormpath.resource.Application)

    def verify_account_email(self, token):

        #TODO: enable auto discovery via Tenant resource (should be just /emailVerificationTokens)
        href = "/accounts/emailVerificationTokens/" + token

        token_dict = {self.HREF_PROP_NAME : href}

        ev_token = self.data_store.instantiate(EmailVerificationToken, token_dict)

        #execute a POST (should clean this up / make it more obvious)
        return self.data_store.save(ev_token, stormpath.resource.Account)


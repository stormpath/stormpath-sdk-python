__author__ = 'ecrisostomo'

import stormpath
from stormpath.resource.resource import InstanceResource, CollectionResource, StatusResource

class Application(InstanceResource, StatusResource):

    NAME = "name"
    DESCRIPTION = "description"
    TENANT = "tenant"
    ACCOUNTS = "accounts"
    PASSWORD_RESET_TOKENS = "passwordResetTokens"

    @property
    def name(self):
        return self.get_property(self.NAME)

    @name.setter
    def name(self, name):
        self._set_property_(self.NAME, name)

    @property
    def description(self):
        return self.get_property(self.DESCRIPTION)

    @description.setter
    def description(self, description):
        self._set_property_(self.DESCRIPTION, description)

    @property
    def tenant(self):
        return self._get_resource_property_(self.TENANT, stormpath.resource.Tenant)

    @property
    def accounts(self):
        return self._get_resource_property_(self.ACCOUNTS, stormpath.resource.AccountList)

    def send_password_reset_email(self, account_username_or_email):
        """
        Sends a password reset email for the specified account username or email address.  The email will contain
        a password reset link that the user can click or copy into their browser address bar.

        This method merely sends the password reset email that contains the link and nothing else.  You will need to
        handle the link requests and then reset the account's password as described in the
        verify_password_reset_token method's docstring.

        :param str account_username_or_email: a username or email address of an Account that may login to the application.

        :returns the Account corresponding to the specified username or email address.
        """
        password_reset_token = self._create_password_reset_token_(account_username_or_email)
        return password_reset_token.account

    def verify_password_reset_token(self, token):
        """
        Verifies a password reset token in a user-clicked link within an email.

       -Base Link Configuration

           You need to define the *Base* link that will process HTTP requests when users click the link in the
           email as part of your Application's Workflow Configuration within the Stormpath UI Console.  It must be a URL
           served by your application's web servers.  For example:

            https://www.myApplication.com/passwordReset

       -Runtime Link Processing

           When an application user clicks on the link in the email at runtime, your web server needs to process the request
           and look for an *spToken* request parameter.  You can then verify the *pToken*, and then finally
           change the Account's password.

       Usage Example:

       Browser:

         *GET https://www.myApplication/passwordReset?spToken=someTokenValueHere*

       Your code:

        token = #get the spToken query parameter

        account = application.verify_password_reset_token(token)

       # token has been verified - now set the new password with what the end-user submits:
       account.password = 'user_submitted_new_password'
       account.save


       :param str token: the verification token, usually obtained as a request parameter by your application.

       :returns the Account matching the specified token.
        """

        href = self._password_reset_token_href_() + '/' + token

        password_reset_token = self.data_store.instantiate(stormpath.resource.PasswordResetToken, {self.HREF_PROP_NAME : href})

        return password_reset_token.account

    def authenticate_account(self, request):
        """
        Authenticates an account's submitted principals and credentials (e.g. username and password).  The account must
        be in one of the Application's "assigned Login Sources":http://www.stormpath.com/docs/managing-applications-login-sources.
        If not in an assigned login source, the authentication attempt will fail.
        -Example
        Consider the following username/password-based example:

            request = UsernamePasswordRequest.new username, submittedRawPlaintextPassword, nil
            account = appToTest.authenticate_account(request).get_account


        :param UsernamePasswordRequest request: the authentication request representing an account's principals and credentials (e.g.
                       username/password) used to verify their identity.
        :returns the result of the authentication.  The authenticated account can be obtained from code result. AuthenticationResult#account.

        :raises ResourceError if the authentication attempt fails.
        """
        authenticator = stormpath.auth.BasicAuthenticator(self.data_store)
        return authenticator.authenticate(self.href, request)

    def _create_password_reset_token_(self, email):

        href = self._password_reset_token_href_()

        password_reset_token = self.data_store.instantiate(stormpath.resource.PasswordResetToken, {'email' : email})

        return self.data_store.create(href, password_reset_token, stormpath.resource.PasswordResetToken)

    def _password_reset_token_href_(self):

        password_reset_tokens_href = self.get_property(self.PASSWORD_RESET_TOKENS)

        if(password_reset_tokens_href):
            return password_reset_tokens_href[self.HREF_PROP_NAME]

class ApplicationList(CollectionResource):

    @property
    def item_type(self):
        return Application


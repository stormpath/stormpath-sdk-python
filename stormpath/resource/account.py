import json
from . import Resource, ResourceList, API_URL
from .directory import Directory
from stormpath.error import Error as StormpathError

class Account(Resource):
    """
    Account resource:
    https://www.stormpath.com/docs/rest/api#Accounts

    """

    path = 'accounts'
    fields = ['username', 'email', 'password', 'givenName',
            'middleName', 'surname', 'status',]

    def __str__(self):
        return self.username

    @staticmethod
    def prepare_data(data):
        """
        Maps python style names to Stormpath API names for Account.

        """
        clean_data = {}
        for k,v in data.items():
            if k == 'given_name':
                clean_data['givenName'] = v
            elif k == 'middle_name':
                clean_data['middleName'] = v
            else:
                clean_data[k] = v

        return clean_data

    @property
    def password_reset_token(self):
        return self._password_reset_token

    @password_reset_token.setter
    def password_reset_token(self, token):
        self._password_reset_token = token

    @property
    def email_verification_token(self):
        return self._email_verification_token

    @email_verification_token.setter
    def email_verification_token(self, token):
        self._email_verification_token = token

    @property
    def directory(self):
        """
        Returns directory related to this Account.

        """

        self.read()
        url = self._data['directory']['href']
        directory = Directory(session=self._session, url=url)
        directory.read()
        return directory

    def add_group(self, group):
        """
        Creates and returns a new GroupMembership which connects this account and group.

        """

        from .group_membership import GroupMembership
        gm = GroupMembership(session=self._session, account=self, group=group)
        gm.save()
        return gm

    @property
    def groups(self):
        """
        Returns a GroupResourceList related to this directory.

        """

        from .group import Group, GroupResourceList
        if not self._data:
            self.read()

        url = self._data['groups']['href']
        return GroupResourceList(url=url, session=self._session,\
                resource=Group, directory=self.directory)

    @property
    def group_memberships(self):
        """
        Returns a GroupMembershipResourceList related to this directory.

        """

        from .group_membership import GroupMembership, GroupMembershipResourceList
        url = '%s/groupMemberships' % self.url
        return GroupMembershipResourceList(url=url, session=self._session,\
                resource=GroupMembership)

class AccountResourceList(ResourceList):
    """
    List of Account resources.

    """

    def __init__(self, *args, **kwargs):
        if 'directory' in kwargs.keys():
            self._directory = kwargs.pop('directory')

        if 'group' in kwargs.keys():
            self._group = kwargs.pop('group')

        super(AccountResourceList, self).__init__(*args, **kwargs)

    def create(self, *args, **kwargs):
        """
        Creates a new Account in a specific Directory.

        """

        if self._directory:
            # handle creation in directory
            url = '%sdirectories/%s/accounts' % (API_URL, self._directory.uid)

            if len(args) == 1:
                data = args[0]
            elif len(args) == 2:
                data = args[0]
                url = url + args[1]
            else:
                data = kwargs.get('data') or kwargs
            data = self._resource_class.prepare_data(data)

            resp = self._session.post(url, data=json.dumps(data))
            if resp.status_code not in (200, 201):
                raise StormpathError(error=resp.json())

            try:
                token_url = resp.json().get('emailVerificationToken')
                token = None
                if token_url:
                    token = token_url.get('href').split('/')[-1]
            except:
                # FIXME: unknown exception
                raise NotImplementedError

            account = Account(session=self._session, data=resp.json())
            account.email_verification_token = token
            return account
        else:
            raise NotImplementedError

    def verify_email_token(self, token):
        """
        Verifies account creation

        """
        path = "accounts/emailVerificationTokens/%s" % (token)
        url = "%s%s" % (API_URL, path)

        resp = self._session.post(url=url)
        if resp.status_code != 200:
            raise StormpathError(resp.json())

        account = Account(session=self._session, url=resp.json().get('href'))
        return account

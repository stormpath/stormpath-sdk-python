import jprops
import json
from requests.auth import HTTPBasicAuth, HTTPDigestAuth

class Auth(object):
    """
    Auth class is used to provide a proper authentication for requests library
    based on any valid authentication source with Stormpath API key.

    """

    def __init__(self, api_key_file_location=None,
            api_key_id_property_name=None, api_key_secret_property_name=None,
            api_key=None, api_id=None, api_secret=None, api_url=None,
            **kwargs):
        """
        Checks various authentication sources for an API key and 
        uses first available.

        """

        self._id = None
        self._secret = None

        # if `api_key_file_location` is available extract key/secret
        # and ignore other authentication sources
        if api_key_file_location:
            with open(api_key_file_location, 'r') as fp:
                cred = jprops.load_properties(fp)
                self._id = cred.get('apiKey.id')
                self._secret = cred.get('apiKey.secret')
                del cred
            return

        # if `api_key` is available extract key/secret
        # and ignore other authentication sources
        if api_key:
            self._id, self._secret = api_key.get('id'), api_key.get('secret')
            return

        # if `api_id` and `api_secret` are available use them
        # and ignore other authentication sources
        if api_id and api_secret:
            self._id, self._secret = api_id, api_secret
            return

        raise Exception('Valid authentication source not found.')

    def __call__(self):
        return self.basic

    @property
    def id(self):
        return self._id

    @property
    def secret(self):
        return self._secret

    def clear(self):
        """
        Clear id/secret for security purposes
        FIXME: should check requirements
        """
        raise NotImplementedError

    @property
    def basic(self):
        return HTTPBasicAuth(self._id, self._secret)

    @property
    def digest(self):
        raise NotImplementedError
        # not http digest alg., import Sauthc1Signer from old SDK
        # and implement requests custom auth.

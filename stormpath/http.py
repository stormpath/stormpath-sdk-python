import json
from collections import OrderedDict
from requests import Session
from .error import Error

from stormpath import __version__ as STORMPATH_VERSION


class HttpExecutor(object):
    """Handles the actual HTTP requests to the Stormpath service.

    It uses the Requests library: http://docs.python-requests.org/en/latest/.
    The HttpExecutor, along with :class:`stormpath.cache.manager.CacheManager`
    is a part of the :class:`stormpath.data_store.DataStore`.

    :param base_url: The root of the Stormpath service.
        Paths to specific resources will be prepended by this url.

    :param auth: Authentication manager, like
        :class:`stormpath.auth.Sauthc1Signer`.
    """

    USER_AGENT = 'Stormpath-PythonSDK/' + STORMPATH_VERSION

    def __init__(self, base_url, auth):

        self.session = Session()
        self.base_url = base_url
        self.session.auth = auth
        self.session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'User-Agent': self.USER_AGENT
        })

    def request(self, method, url, data=None, params=None):
        if params:
            params = OrderedDict(sorted(params.items()))

        if not url.startswith(self.base_url):
            url = self.base_url + url

        try:
            r = self.session.request(method, url, data=data, params=params,
                allow_redirects=False)
        except Exception as ex:
            raise Error({'developerMessage': str(ex)})

        if r.status_code in [301, 302] and 'location' in r.headers:
            return self.request('GET', r.headers['location'], params=params)

        if r.status_code not in [200, 201, 204]:
            raise Error(r.json(), http_status=r.status_code)

        try:
            return r.json()
        except:
            return {}

    def get(self, url, params=None):
        return self.request('GET', url, params=params)

    def post(self, url, data, params=None):
        return self.request('POST', url, data=json.dumps(data), params=params)

    def delete(self, url):
        return self.request('DELETE', url)

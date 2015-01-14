"""HTTP request handling utilities."""


from collections import OrderedDict
from json import dumps
from platform import platform, mac_ver, win32_ver, linux_distribution, system
from requests import Session
from sys import version_info as vi

from stormpath import __version__ as STORMPATH_VERSION
from .error import Error


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
    os_info = platform()
    os_versions = {
        'Linux': "%s (%s)" % (linux_distribution()[0], os_info),
        'Windows': "%s (%s)" % (win32_ver()[0], os_info),
        'Darwin': "%s (%s)" % (mac_ver()[0], os_info),
    }

    USER_AGENT = 'stormpath-sdk-python/%s python/%s %s/%s' % (
        STORMPATH_VERSION,
        '%s.%s.%s' % (vi.major, vi.minor, vi.micro),
        system(),
        os_versions.get(system(), ''),
    )

    def __init__(self, base_url, auth, proxies=None, user_agent=None):
        # If a custom user agent is specified, we'll append it to the end of
        # our built-in user agent.  This way we'll get very detailed user agent
        # strings.
        if user_agent is not None:
            self.USER_AGENT = user_agent + ' ' + self.USER_AGENT

        self.base_url = base_url
        self.session = Session()
        self.session.proxies = proxies or {}
        self.session.auth = auth
        self.session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'User-Agent': self.USER_AGENT,
        })

    def request(self, method, url, data=None, params=None):
        if params:
            params = OrderedDict(sorted(params.items()))

        if not url.startswith(self.base_url):
            url = self.base_url + url

        import logging
        log = logging.getLogger(__name__)

        try:
            r = self.session.request(method, url, data=data, params=params,
                allow_redirects=False, verify=False)
        except Exception as ex:
            raise Error({'developerMessage': str(ex)})

        log.debug('HttpExecutor.request(method=%s, url=%s, params=%s, data=%s) -> [%d] %s' %
            (method, url, repr(params), repr(data), r.status_code, r.text))

        if r.status_code in [301, 302] and 'location' in r.headers:
            return self.request('GET', r.headers['location'], params=params)

        if r.status_code >= 400 and r.status_code <= 600:
            try:
                ret = r.json()
            except ValueError:
                ret = "An unexpected error occurred."
            raise Error(ret, http_status=r.status_code)

        try:
            d = r.json()
            d['sp_http_status'] = r.status_code
            return d
        except Exception:
            return {}

    def get(self, url, params=None):
        return self.request('GET', url, params=params)

    def post(self, url, data, params=None):
        return self.request('POST', url, data=dumps(data), params=params)

    def delete(self, url):
        return self.request('DELETE', url)

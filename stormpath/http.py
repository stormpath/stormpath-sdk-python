"""HTTP request handling utilities."""

import cgi
import time
import random

from collections import OrderedDict
from json import dumps
from requests import Session
from requests.exceptions import RequestException
from sys import version_info as vi

# Hack for Google App Engine
# GAE doesn't allow users to import `win32_ver` as it's sandbox mode rips
# `_winreg` out of the standard library :(  This patch works by creating a stub
# replacement for it that won't error.
try:
    from platform import platform, mac_ver, win32_ver, linux_distribution, system
except ImportError:
    win32_ver = lambda: ('', '', '', '')


from stormpath import __version__ as STORMPATH_VERSION
from .error import Error


import logging
log = logging.getLogger(__name__)


class HttpExecutor(object):
    """Handles the actual HTTP requests to the Stormpath service.

    It uses the Requests library: http://docs.python-requests.org/en/latest/.
    The HttpExecutor, along with :class:`stormpath.cache.manager.CacheManager`
    is a part of the :class:`stormpath.data_store.DataStore`.

    :param base_url: The root of the Stormpath service.
        Paths to specific resources will be prepended by this url.

    :param auth: Authentication manager, like
        :class:`stormpath.auth.Sauthc1Signer`.
    :param get_delay: A Function that will return the number of milliseconds
        to wait before retrying the request. The function must take one parameter
        which is the number of retries already done. If no function is supplied
        the default backoff strategy is used (see the pause_exponentially method).
    """
    DEFAULT_MAX_RETRIES = 4
    MAX_BACKOFF_IN_MILLISECONDS = 20 * 1000

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

    def __init__(self, base_url, auth, proxies=None, user_agent=None, get_delay=None):
        # If a custom user agent is specified, we'll append it to the end of
        # our built-in user agent.  This way we'll get very detailed user agent
        # strings.
        if user_agent is not None:
            self.USER_AGENT = user_agent + ' ' + self.USER_AGENT

        self.get_delay = get_delay
        self.base_url = base_url
        self.session = Session()
        self.session.proxies = proxies or {}
        self.session.auth = auth
        self.session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'User-Agent': self.USER_AGENT,
        })

    def is_throttling_or_unexpected_error(self, status):
        """Helper method for determining if the request was told to back off,
        or if an unexpected error in the 5xx range occured."""

        if isinstance(status, RequestException):
            return True
        elif isinstance(status, int) and (status == 429 or status >= 500):
            return True
        else:
            return False

    def pause_exponentially(self, retries):
        """Helper method for calculating the number of milliseconds to sleep
        before re-trying a request."""

        if self.get_delay is not None:
            delay = self.get_delay(retries)
        else:
            scale_factor = 500 + random.randint(1, 100)
            delay = 2 ** retries * scale_factor

        delay = min(delay, self.MAX_BACKOFF_IN_MILLISECONDS)

        log.debug("Retryable condition detected, will retry in %s ms, attempt number: %s" % (delay, retries))

        # sleep in seconds
        time.sleep(delay / float(1000))

    def should_retry(self, retries, status):
        """Helper method for deciding if a request should be retried."""
        if self.is_throttling_or_unexpected_error(status):
            if retries < self.DEFAULT_MAX_RETRIES:
                return True
        return False

    def raise_error(self, r):
        try:
            ret = r.json()
        except ValueError as e:
            ret = "An unexpected error occurred. HTTP Status code: %s. " % r.status_code
            ret += "Error message: %s. " % e
            ret += "Consider setting the logging level to debug for more detail."
        raise Error({'developerMessage': ret}, http_status=r.status_code)

    def return_response(self, r):
        if not r.text:
            return {}
        try:
            d = r.json()
            d['sp_http_status'] = r.status_code
        except ValueError:
            d = {}
            d['content'] = r.content
            _, params = cgi.parse_header(
                r.headers.get('Content-Disposition', ''))
            d['filename'] = params.get('filename')
        return d

    def request(self, method, url, data=None, params=None, retry_count=0):
        if params:
            params = OrderedDict(sorted(params.items()))

        if not url.startswith(self.base_url):
            url = self.base_url + url

        try:
            r = self.session.request(method, url, data=data, params=params,
                allow_redirects=False)
        except Exception as e:
            if self.should_retry(retry_count, e):
                self.pause_exponentially(retry_count)
                self.request(method, url, data=data, params=params, retry_count=retry_count + 1)
            raise Error({'developerMessage': str(e)})

        log.debug('HttpExecutor.request(method=%s, url=%s, params=%s, data=%s) -> [%d] %s' %
            (method, url, repr(params), repr(data), r.status_code, r.text))

        if r.status_code in [301, 302] and 'location' in r.headers:
            if not r.headers['location'].startswith(self.base_url):
                message = 'Trying to redirect outside of API base url: %s' % \
                    r.headers['location']
                raise Error({'developerMessage': message} )
            return self.request('GET', r.headers['location'], params=params)

        if r.status_code >= 400 and r.status_code <= 600:
            if self.should_retry(retry_count, r.status_code):
                self.pause_exponentially(retry_count)
                self.request(method, url, data=data, params=params, retry_count=retry_count + 1)
            else:
                self.raise_error(r)

        return self.return_response(r)

    def get(self, url, params=None):
        return self.request('GET', url, params=params)

    def post(self, url, data, params=None):
        return self.request('POST', url, data=dumps(data), params=params)

    def delete(self, url):
        return self.request('DELETE', url)

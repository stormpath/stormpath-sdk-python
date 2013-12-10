from unittest import TestCase, main
from collections import OrderedDict
from stormpath.http import HttpExecutor
from stormpath.error import Error
from stormpath.client import Client

from stormpath import __version__ as STORMPATH_VERSION

try:
    from mock import patch, MagicMock, PropertyMock
except ImportError:
    from unittest.mock import patch, MagicMock, PropertyMock


class HttpTest(TestCase):

    @patch('stormpath.http.Session')
    def test_session_init(self, Session):
        s = Session.return_value
        s.headers = {}

        HttpExecutor('http://api.stormpath.com/v1', ('user', 'pass'))

        self.assertEqual(s.auth, ('user', 'pass'))
        self.assertEqual(s.headers['Content-Type'], 'application/json')
        self.assertEqual(s.headers['User-Agent'], 'Stormpath-PythonSDK/' +
            STORMPATH_VERSION)

    @patch('stormpath.http.Session')
    def test_get_request(self, Session):
        s = Session.return_value
        s.request.return_value.status_code = 200

        ex = HttpExecutor('http://api.stormpath.com/v1', ('user', 'pass'))
        data = ex.get('/test', {'q': 'foo'})

        s.request.assert_called_once_with('GET',
            'http://api.stormpath.com/v1/test',
            data=None, params={'q': 'foo'}, allow_redirects=False)

        self.assertEqual(data, s.request.return_value.json.return_value)

    @patch('stormpath.http.Session')
    def test_get_request_error(self, Session):
        s = Session.return_value
        s.request.return_value.status_code = 400
        s.request.return_value.json.return_value = None

        ex = HttpExecutor('http://api.stormpath.com/v1', ('user', 'pass'))

        with self.assertRaises(Error):
            ex.get('/test')

    @patch('stormpath.http.Session')
    def test_follow_redirects(self, Session):

        def redirector(method, url, data, params, allow_redirects=None):
            if url.endswith('/first'):
                return MagicMock(status_code=302, headers={
                    'location': '/second'})
            elif url.endswith('/second'):
                return MagicMock(status_code=200,
                    json=MagicMock(return_value={'hello': 'World'}))

        Session.return_value = MagicMock(request=redirector)
        ex = HttpExecutor('http://api.stormpath.com/v1', ('user', 'pass'))

        data = ex.get('/first')

        self.assertEqual(data, {'hello': 'World'})

    @patch('stormpath.http.Session')
    def test_sauthc1_dict(self, Session):
        Session.return_value.request.return_value = \
            MagicMock(status_code=200,
                json=MagicMock(return_value={'hello': 'World'}))

        ex = HttpExecutor('http://api.stormpath.com/v1', ('user', 'pass'))
        params = OrderedDict([('username', 'username'),
            ('email', 'email'), ('password', 'password')])
        ex.get('/resource', params=params)

        Session.return_value.request.assert_called_once_with('GET',
            'http://api.stormpath.com/v1/resource',
            params=OrderedDict([
                ('email', 'email'),
                ('password', 'password'),
                ('username', 'username')]),
            allow_redirects=False, data=None)

    @patch('stormpath.client.Auth.digest', new_callable=PropertyMock)
    @patch('stormpath.http.Session')
    def test_proxies(self, session, auth):
        proxies = {
            'https': 'https://i-am-so-secure.com',
            'http': 'http://i-want-to-be.secure.org'}
        client = Client(api_key={'id': 'MyId', 'secret': 'Shush!'},
            proxies=proxies)
        self.assertEqual(client.data_store.executor.session.proxies, proxies)

        client = Client(api_key={'id': 'MyId', 'secret': 'Shush!'})
        self.assertEqual(client.data_store.executor.session.proxies, {})

if __name__ == '__main__':
    main()

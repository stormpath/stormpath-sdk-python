from unittest import TestCase, main
from stormpath.http import HttpExecutor
from stormpath.error import Error

from stormpath import __version__ as STORMPATH_VERSION

try:
    from mock import patch, MagicMock
except ImportError:
    from unittest.mock import patch, MagicMock

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
            data=None, params={'q': 'foo'})

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

        def redirector(method, url, data, params):
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

if __name__ == '__main__':
    main()

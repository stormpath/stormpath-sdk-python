
from unittest import TestCase, main
from collections import OrderedDict
from requests import RequestException
from stormpath.http import HttpExecutor
from stormpath.error import Error
from stormpath.client import Client

try:
    from mock import patch, MagicMock, PropertyMock, call
except ImportError:
    from unittest.mock import patch, MagicMock, PropertyMock, call


class HttpTest(TestCase):

    @patch('stormpath.http.Session')
    def test_session_init(self, Session):
        s = Session.return_value
        s.headers = {}

        HttpExecutor('http://api.stormpath.com/v1', ('user', 'pass'))

        self.assertEqual(s.auth, ('user', 'pass'))
        self.assertEqual(s.headers['Content-Type'], 'application/json')
        self.assertEqual(s.headers['User-Agent'], HttpExecutor.USER_AGENT)

    @patch('stormpath.http.Session')
    def test_get_request(self, Session):
        s = Session.return_value
        s.request.return_value.status_code = 200

        ex = HttpExecutor('http://api.stormpath.com/v1', ('user', 'pass'))
        data = ex.get('/test', {'q': 'foo'})

        s.request.assert_called_once_with(
            'GET', 'http://api.stormpath.com/v1/test', data=None,
            params={'q': 'foo'}, headers=None, allow_redirects=False)

        self.assertEqual(data, s.request.return_value.json.return_value)

    @patch('stormpath.http.Session')
    def test_get_binary_request(self, Session):
        s = Session.return_value
        s.request.return_value.json.side_effect = ValueError
        s.request.return_value.status_code = 200
        s.request.return_value.content = 'some content'
        s.request.return_value.headers = {
            'Content-Disposition': 'attachment; filename="some_archive.zip"'}

        ex = HttpExecutor('http://api.stormpath.com/v1', ('user', 'pass'))
        data = ex.get('/test')

        self.assertEqual(
            data, {'content': 'some content', 'filename': 'some_archive.zip'})

    @patch('stormpath.http.Session')
    def test_get_request_error(self, Session):
        s = Session.return_value
        s.request.return_value.status_code = 400
        s.request.return_value.json.return_value = None

        ex = HttpExecutor('http://api.stormpath.com/v1', ('user', 'pass'))

        with self.assertRaises(Error):
            ex.get('/test')

    @patch('stormpath.http.Session')
    def test_get_request_exception_and_retry_and_success(self, Session):
        self.count = 0
        request_exception = RequestException('I raise RequestException!')
        def exception_raiser(method, url, data, params, headers=None,
                             allow_redirects=None):
            if self.count < 4:
                self.count += 1
                raise request_exception

            return MagicMock(
                status_code=200,
                json=MagicMock(return_value={'success': 'True'}))

        Session.return_value = MagicMock(request=exception_raiser)

        ex = HttpExecutor('http://api.stormpath.com/v1', ('user', 'pass'))

        ShouldRetry = MagicMock(return_value=True)

        with patch('stormpath.http.HttpExecutor.should_retry', ShouldRetry):
            with self.assertRaises(Error):
                ex.get('/test')

        should_retry_calls = [
            call(0, request_exception), call(1, request_exception),
            call(2, request_exception), call(3, request_exception),
        ]
        ShouldRetry.assert_has_calls(should_retry_calls)

    @patch('stormpath.http.Session')
    def test_get_request_exception_and_retry_four_times(self, Session):
        request_exception = RequestException('I raise RequestException!')
        def exception_raiser(method, url, data, params, headers=None,
                             allow_redirects=None):
            raise request_exception

        Session.return_value = MagicMock(request=exception_raiser)

        ex = HttpExecutor('http://api.stormpath.com/v1', ('user', 'pass'))

        def try_four_times(retries, status):
            return retries <= 3

        ShouldRetry = MagicMock()
        ShouldRetry.side_effect = try_four_times

        with patch('stormpath.http.HttpExecutor.should_retry', ShouldRetry):
            with self.assertRaises(Error):
                ex.get('/test')

        should_retry_calls = [
            call(0, request_exception), call(1, request_exception),
            call(2, request_exception), call(3, request_exception),
            call(4, request_exception)
        ]
        ShouldRetry.assert_has_calls(should_retry_calls)


    @patch('stormpath.http.Session')
    def test_follow_redirects(self, Session):

        def redirector(method, url, data, params, headers=None,
                       allow_redirects=None):
            if url.endswith('/first'):
                return MagicMock(status_code=302, headers={
                    'location': 'http://api.stormpath.com/v1/second'})
            elif url.endswith('/second'):
                return MagicMock(status_code=200,
                    json=MagicMock(return_value={'hello': 'World'}))

        Session.return_value = MagicMock(request=redirector)
        ex = HttpExecutor('http://api.stormpath.com/v1', ('user', 'pass'))

        data = ex.get('/first')

        self.assertEqual(data, {'hello': 'World', 'sp_http_status': 200})

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
            headers=None, allow_redirects=False, data=None)

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

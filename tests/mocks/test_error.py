from unittest import TestCase, main
from stormpath.error import Error


class ErrorTest(TestCase):

    def test_error_parsing(self):
        err_dict = {
            "status": 404,
            "code": 404,
            "message": "Oops! The application you specified cannot be found.",
            "developerMessage": "The specified Application cannot be found...",
            "moreInfo": "http://www.stormpath.com/docs/errors/404"
        }
        e = Error(err_dict)

        self.assertEqual(e.status, 404)
        self.assertEqual(e.code, 404)
        self.assertEqual(e.message,
            "The specified Application cannot be found...")
        self.assertEqual(e.developer_message,
            "The specified Application cannot be found...")
        self.assertEqual(e.user_message,
            "Oops! The application you specified cannot be found.")
        self.assertEqual(e.more_info,
            "http://www.stormpath.com/docs/errors/404")

    def test_graceful_invalid_error_parsing(self):
        e = Error({})

        self.assertEqual(e.status, -1)
        self.assertEqual(e.code, -1)

    def test_null_response_error_parsing(self):
        e = Error(None)

        self.assertEqual(e.status, -1)
        self.assertEqual(e.code, -1)

if __name__ == '__main__':
    main()

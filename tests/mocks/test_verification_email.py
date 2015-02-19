""""
Integration tests for various pieces involved in external provider support.
"""

from unittest import TestCase, main

try:
    from mock import MagicMock
except ImportError:
    from unittest.mock import MagicMock

from stormpath.resources.account import Account
from stormpath.resources.application import Application
from stormpath.resources.directory import Directory, DirectoryList
from stormpath.resources.verification_email import VerificationEmailList


class TestVerificationEmail(TestCase):

    def test_resend(self):
        ds = MagicMock()
        ds.create_resource.return_value = {}
        client = MagicMock(data_store=ds, BASE_URL='http://example.com/')

        acc = Account(
            client=client,
            properties={'href': 'test/app','email': 'some@email.com'})
        vel = VerificationEmailList(client=client, href='test/emails')
        app = Application(
            client=client,
            properties={'href': 'test/app','verification_emails': vel})
        dir = Directory(client=client, href='test/directory')

        app.verification_emails.resend(acc, dir)

        ds.create_resource.assert_called_once_with(
            'http://example.com/test/emails',
            {'login': 'some@email.com', 'account_store': 'test/directory'})


if __name__ == '__main__':
    main()

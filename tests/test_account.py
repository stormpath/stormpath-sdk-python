import unittest
from tests.test_base import BaseTest


class TestAccount(BaseTest):

    def test_properties(self):

        directory = self.client.directories.get(self.dir_href)
        username, email = 'superuser123', 'superuser123@superemail.comy'
        given_name, surname, dir_name = 'Super', 'User', 'New Dir Name 123 Ha!'
        password = 'superP4ss'
        account = directory.accounts.create({
            'username': username,
            'email': email,
            'given_name': given_name,
            'surname': surname,
            'password': password
        })

        self.assertEqual(account.username, username)
        self.assertEqual(account.email, email)
        self.assertEqual(account.given_name, given_name)
        self.assertEqual(account.surname, surname)

if __name__ == '__main__':
    unittest.main()

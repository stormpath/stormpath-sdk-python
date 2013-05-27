import unittest
from tests.test_base import BaseTest


class TestTenant(BaseTest):

    def test_properties(self):
        self.assertIsNotNone(self.client.tenant.href)
        self.assertIsNotNone(self.client.tenant.name)
        self.assertIsNotNone(self.client.applications)
        self.assertIsNotNone(self.client.directories)

    def test_get_url(self):
        application = self.client.applications.get(self.app_href)
        self.assertEqual(application.href, self.app_href)

        directory = self.client.directories.get(self.dir_href)
        self.assertEqual(directory.href, self.dir_href)

if __name__ == '__main__':
    unittest.main()

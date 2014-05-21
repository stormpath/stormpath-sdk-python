"""Helpers for running our tests."""


from os import getenv
from unittest import TestCase
from uuid import uuid4

from stormpath.client import Client


class LiveTestCase(TestCase):
    """
    Custom test case which bootstraps a Stormpath client.

    This makes writing tests significantly easier as there's no work to do for
    setUp / tearDown.

    When a test finishes, we'll delete all Stormpath resources that were
    created.
    """
    def setUp(self):
        """
        Automatically creates the following resources:

            - A Stormpath Client.
            - A Stormpath Application.
            - A unique test prefix.
        """
        self.prefix = 'stormpath-test-%s-' % uuid4().hex

        self.client = Client(
            id = getenv('STORMPATH_API_KEY_ID'),
            secret = getenv('STORMPATH_API_KEY_SECRET'),
        )

        self.application = self.client.applications.create({
            'name': self.prefix + 'application',
            'description': 'A temporary Application created during a test run.',
        }, create_directory=True)

    def tearDown(self):
        """
        Automatically removes all resources with the unique test prefix.

        .. note::
            By removing the Applications and Directories we're automatically
            destroying all other resources as by deleting those two top-level
            containers we'll automatically eliminate Accounts, etc.
        """
        for app in self.client.applications.search(self.prefix):
            app.delete()

        for dir in self.client.directories.search(self.prefix):
            dir.delete()

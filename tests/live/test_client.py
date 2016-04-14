"""Live tests of Client functionality."""


from .base import AuthenticatedLiveBase


class TestClientProperties(AuthenticatedLiveBase):
    """Assert all Client properties work as expected."""

    def test_client_api_keys(self):
        current_api_keys = len(self.client.api_keys)

        app = self.client.applications.create({
            'name': self.get_random_name()
        }, create_directory=True)
        account = app.accounts.create({
            'given_name': 'Randall',
            'surname': 'Degges',
            'email': self.get_random_name() + '@example.com',
            'password': 'wootILOVEc00kies!'
        })
        key = account.api_keys.create()

        self.assertEqual(len(self.client.api_keys), current_api_keys + 1)

        key.delete()

        self.assertEqual(len(self.client.api_keys), current_api_keys)

        total_keys_to_create = 150
        for i in range(total_keys_to_create):
            account.api_keys.create()

        self.assertEqual(len(self.client.api_keys), current_api_keys + total_keys_to_create)

        account.delete()

        self.assertEqual(len(self.client.api_keys), current_api_keys)

    def test_client_applications(self):
        current_apps = len(self.client.applications)

        app = self.client.applications.create({'name': self.get_random_name()})

        self.assertEqual(len(self.client.applications), current_apps + 1)

        app.delete()

        self.assertEqual(len(self.client.applications), current_apps)

        total_applications_to_create = 150
        for i in total_applications_to_create:
            self.client.applications.create({'name': self.get_random_name()})

        self.assertEqual(len(self.client.applications), current_apps + 150)

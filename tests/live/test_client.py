"""Live tests of Client functionality."""


from .base import AuthenticatedLiveBase


class TestClientProperties(AuthenticatedLiveBase):
    """Assert all Client properties work as expected."""

    def test_client_applications(self):
        current_apps = len(self.client.applications)

        app = self.client.applications.create({'name': self.get_random_name()})

        self.assertEqual(len(self.client.applications), current_apps + 1)

        app.delete()

        self.assertEqual(len(self.client.applications), current_apps)

        total_applications_to_create = 150
        for i in range(total_applications_to_create):
            self.client.applications.create({'name': self.get_random_name()})

        self.assertEqual(len(self.client.applications), current_apps + 150)

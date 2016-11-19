"""Live tests of Challenge and MFA functionality."""


from .base import MFABase


class TestChallenge(MFABase):

    def setUp(self):
        super(TestChallenge, self).setUp()
        data = {
            'phone': self.phone,
            'type': 'SMS'
        }
        self.factor = self.account.factors.create(properties=data, challenge=False)

    def test_status_create(self):
        # Ensure that the status methods are properly working.
        # Ensure that a newly created challenge has a CREATED status.
        challenge = self.factor.challenge_factor()
        self.assertTrue(challenge.is_created())
        self.assertEqual(challenge.status, 'CREATED')

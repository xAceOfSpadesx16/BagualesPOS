from django.test import TestCase
from django.contrib.auth import get_user_model
from users.models import Profile

User = get_user_model()

class UserSignalsTestCase(TestCase):
    def test_create_profile_signal(self):
        user = User.objects.create_user(username="signaluser", password="password")
        self.assertTrue(hasattr(user, 'profile'))
        self.assertIsInstance(user.profile, Profile)

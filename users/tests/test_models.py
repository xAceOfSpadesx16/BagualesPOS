from django.test import TestCase
from django.contrib.auth import get_user_model
from users.models import Profile

User = get_user_model()

class UserModelTestCase(TestCase):
    def test_create_user_without_username(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(username="", password="password")

    def test_user_str(self):
        user = User.objects.create_user(username="testuser", password="password")
        self.assertEqual(str(user), "testuser")

    def test_profile_creation(self):
        # This also tests the signal indirectly, but good to have explicit checks on model side if needed
        user = User.objects.create_user(username="profileuser", password="password")
        self.assertTrue(Profile.objects.filter(user=user).exists())
        self.assertEqual(str(user.profile), f"Profile object ({user.profile.id})") # Profile doesn't have __str__, checking default or adding one?
        # Profile model doesn't have __str__ method in the file I viewed. 
        # It inherits from Model, so it uses default django __str__. 
        # I won't test __str__ for Profile unless I add it.

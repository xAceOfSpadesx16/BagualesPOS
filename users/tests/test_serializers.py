from django.test import TestCase
from django.contrib.auth import get_user_model
from users.serializers import UserSerializer, CustomTokenObtainPairSerializer

User = get_user_model()

class UserSerializerTestCase(TestCase):
    def test_user_serializer(self):
        user = User.objects.create_user(username="test", email="t@t.com", first_name="Test", last_name="User")
        serializer = UserSerializer(user)
        data = serializer.data
        self.assertEqual(data['username'], "test")
        self.assertEqual(data['email'], "t@t.com")
        self.assertEqual(data['first_name'], "Test")
        self.assertEqual(data['last_name'], "User")

class CustomTokenObtainPairSerializerTestCase(TestCase):
    def test_token_claims(self):
        user = User.objects.create_user(
            username="test", password="password", first_name="Juan", last_name="Perez"
        )
        serializer = CustomTokenObtainPairSerializer()
        token = serializer.get_token(user)
        
        self.assertEqual(token['first_name'], "Juan")
        self.assertEqual(token['last_name'], "Perez")
        self.assertEqual(token['id'], user.id)

class ProfileSerializerTestCase(TestCase):
    def test_profile_serializer(self):
        user = User.objects.create_user(username="profiletest", password="password")
        # Profile is created by signal
        profile = user.profile
        profile.phone_number = "+1234567890"
        profile.save()
        
        from users.serializers import ProfileSerializer
        serializer = ProfileSerializer(profile)
        data = serializer.data
        self.assertEqual(data['phone_number'], "+1234567890")
        self.assertEqual(data['user'], user.id)

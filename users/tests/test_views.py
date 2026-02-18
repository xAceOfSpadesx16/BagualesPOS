from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class UserViewSetTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='admin', password='password', is_staff=True)
        self.client.force_authenticate(user=self.user)
        self.url = reverse('customuser-list')

    def test_list_users(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_permissions(self):
        """MISSING-7: Verify only admin can access UserViewSet"""
        # Create plain user
        user = User.objects.create_user(username='plain', password='password')
        self.client.force_authenticate(user=user)
        
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Admin can access (checked in test_list_users)

    def test_search_users(self):
        # Create another user
        User.objects.create_user(username='otheruser', password='password', first_name="Other", last_name="User")

        # Search by username
        response = self.client.get(self.url, {'search': 'otheruser'})
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['username'], "otheruser")

        # Search by first_name
        response = self.client.get(self.url, {'search': 'Other'})
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['username'], "otheruser")

    def test_ordering_users(self):
        # Create another user
        User.objects.create_user(username='zuser', password='password')

        # Order by username ascending
        response = self.client.get(self.url, {'ordering': 'username'})
        self.assertEqual(response.data['results'][0]['username'], "admin")
        self.assertEqual(response.data['results'][1]['username'], "zuser")

        # Order by username descending
        response = self.client.get(self.url, {'ordering': '-username'})
        self.assertEqual(response.data['results'][0]['username'], "zuser")
        self.assertEqual(response.data['results'][1]['username'], "admin")

class AuthTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpassword', first_name="Test", last_name="User"
        )
        self.token_url = reverse('token_obtain_pair')

    def test_get_token(self):
        data = {
            "username": "testuser",
            "password": "testpassword"
        }
        response = self.client.post(self.token_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        return response.data

    def test_refresh_token(self):
        # 1. Login to get tokens
        token_data = self.test_get_token()
        refresh_token = token_data['refresh']

        # 2. Use refresh token to get new access token
        refresh_url = reverse('token_refresh')
        data = {'refresh': refresh_token}
        response = self.client.post(refresh_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        # With ROTATE_REFRESH_TOKENS=True, we might get a new refresh token too
        if 'refresh' in response.data:
             self.assertNotEqual(refresh_token, response.data['refresh'])

    def test_logout(self):
        # 1. Login
        token_data = self.test_get_token()
        refresh_token = token_data['refresh']
        access_token = token_data['access']

        # 2. Logout (blacklist the refresh token)
        logout_url = reverse('token_logout')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        data = {'refresh': refresh_token}
        response = self.client.post(logout_url, data)

        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)

        # 3. Verify refresh token is blacklisted (cannot be used to refresh)
        self.client.credentials() # Clear auth headers
        refresh_url = reverse('token_refresh')
        response = self.client.post(refresh_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(str(response.data['detail']), 'El token está en la lista negra')

    def test_logout_exception(self):
        from unittest.mock import patch
        
        # 1. Login
        token_data = self.test_get_token()
        refresh_token = token_data['refresh']
        access_token = token_data['access']

        # 2. Logout with mocked exception
        logout_url = reverse('token_logout')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        data = {'refresh': refresh_token}
        
        with patch('users.views.RefreshToken') as mock_refresh:
            mock_refresh.side_effect = Exception("Mocked Exception")
            response = self.client.post(logout_url, data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

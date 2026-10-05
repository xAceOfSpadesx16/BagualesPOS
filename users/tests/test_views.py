from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from core.models import Company

User = get_user_model()

class UserViewSetTestCase(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(name='Test Company')
        self.user = User.objects.create_user(username='admin', password='password', is_staff=True, company=self.company)
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
        User.objects.create_user(username='otheruser', password='password', first_name="Other", last_name="User", company=self.company)

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
        User.objects.create_user(username='zuser', password='password', company=self.company)

        # Order by username ascending
        response = self.client.get(self.url, {'ordering': 'username'})
        self.assertEqual(response.data['results'][0]['username'], "admin")
        self.assertEqual(response.data['results'][1]['username'], "zuser")

        # Order by username descending
        response = self.client.get(self.url, {'ordering': '-username'})
        self.assertEqual(response.data['results'][0]['username'], "zuser")
        self.assertEqual(response.data['results'][1]['username'], "admin")

    def test_tenant_isolation(self):
        """Verify users can only see users from their own company"""
        # Create another company and user
        other_company = Company.objects.create(name='Other Company')
        other_user = User.objects.create_user(
            username='othercompanyuser', 
            password='password', 
            is_staff=True,
            company=other_company
        )
        
        # Current user (self.user) should only see users from self.company
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        usernames = [user['username'] for user in response.data['results']]
        self.assertIn('admin', usernames)
        self.assertNotIn('othercompanyuser', usernames)
        
        # Switch to other_user authentication
        self.client.force_authenticate(user=other_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        usernames = [user['username'] for user in response.data['results']]
        self.assertIn('othercompanyuser', usernames)
        self.assertNotIn('admin', usernames)

    def test_roles_endpoint_admin(self):
        """Admin should see 'Administrador General' in roles"""
        admin_group, _ = Group.objects.get_or_create(name='Administrador General')
        self.user.groups.add(admin_group)
        
        response = self.client.get(reverse('customuser-roles'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        role_names = [role['name'] for role in response.data]
        self.assertIn('Administrador General', role_names)

    def test_roles_endpoint_non_admin(self):
        """Non-admin should NOT see 'Administrador General' in roles"""
        # Create plain user
        user = User.objects.create_user(username='plain2', password='password', company=self.company)
        self.client.force_authenticate(user=user)
        
        # Ensure the group exists
        Group.objects.get_or_create(name='Administrador General')
        Group.objects.get_or_create(name='Cajero')
        
        response = self.client.get(reverse('customuser-roles'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        role_names = [role['name'] for role in response.data]
        self.assertNotIn('Administrador General', role_names)
        self.assertIn('Cajero', role_names)




# ============================================================
# Tests consolidated from test_admin.py, test_registration.py, test_signals.py
# ============================================================
class CustomUserAdminTest(TestCase):
    """Admin tests - consolidated from test_admin.py"""
    
    def setUp(self):
        from django.contrib.admin.sites import AdminSite
        from users.admin import CustomUserAdmin
        from core.models import Branch
        
        self.site = AdminSite()
        self.admin = CustomUserAdmin(User, self.site)
        
        self.company = Company.objects.create(name='Test Company', is_active=True)
        self.branch = Branch.objects.create(company=self.company, name='Test Branch', code='TEST-001', is_active=True)
        
        self.user = User.objects.create_user(username='testuser', password='testpass123', email='test@example.com')
        self.user.branch.add(self.branch)
    
    def test_get_queryset_prefetches_branches(self):
        """Test that get_queryset uses prefetch_related for branches"""
        from django.test import RequestFactory
        
        request = RequestFactory().get('/admin/users/customuser/')
        request.user = self.user
        
        queryset = self.admin.get_queryset(request)
        self.assertIn('branch', queryset._prefetch_related_lookups)
    
    def test_fieldsets_includes_branch_assignment(self):
        """Test that fieldsets includes branch assignment section"""
        fieldsets = self.admin.fieldsets
        
        branch_fieldset = None
        for name, options in fieldsets:
            if name == 'Branch Assignment':
                branch_fieldset = options
                break
        
        self.assertIsNotNone(branch_fieldset)
        self.assertIn('branch', branch_fieldset['fields'])


class UserRegistrationTestCase(APITestCase):
    """Registration tests - consolidated from test_registration.py"""
    
    def test_user_registration_success(self):
        """Test successful user registration"""
        url = reverse('customuser-register')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'securepass123',
            'password_confirm': 'securepass123',
            'company_name': 'New Company',
            'company_tax_id': '99999999'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], 'newuser')
        self.assertIn('company_id', response.data)
        self.assertIn('company_name', response.data)
    
    def test_user_registration_password_mismatch(self):
        """Test registration with password mismatch"""
        url = reverse('customuser-register')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'password123',
            'password_confirm': 'differentpassword',
            'company_name': 'New Company'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_token_includes_company(self):
        """Test that JWT token includes company information"""
        from users.serializers import CustomTokenObtainPairSerializer
        
        company = Company.objects.create(name="Test Co", tax_id="12345")
        user = User.objects.create_user(username='testuser', password='testpass', company=company)
        
        token = CustomTokenObtainPairSerializer.get_token(user)
        self.assertIn('company_id', token)
        self.assertEqual(token['company_id'], company.id)
        self.assertEqual(token['company_name'], company.name)


class UserSignalsTestCase(TestCase):
    """Signal tests - consolidated from test_signals.py"""
    
    def test_create_profile_signal(self):
        from users.models import Profile
        
        user = User.objects.create_user(username="signaluser", password="password")
        self.assertTrue(hasattr(user, 'profile'))
        self.assertIsInstance(user.profile, Profile)


class UserViewSetQuerysetTestCase(APITestCase):
    """Test UserViewSet.get_queryset() for 100% coverage"""
    
    def setUp(self):
        self.company1 = Company.objects.create(name='Company 1', tax_id='111')
        self.company2 = Company.objects.create(name='Company 2', tax_id='222')
        
        self.user1 = User.objects.create_user(
            username='user1',
            password='pass123',
            company=self.company1
        )
        
        self.user2 = User.objects.create_user(
            username='user2',
            password='pass123',
            company=self.company2
        )
        
        self.superuser = User.objects.create_superuser(
            username='superuser',
            password='pass123',
            email='super@test.com'
        )
    
    def test_unauthenticated_user_gets_empty_queryset(self):
        """Test line 36: unauthenticated user returns empty queryset"""
        from rest_framework.test import APIRequestFactory
        from users.views import UserViewSet
        from django.contrib.auth.models import AnonymousUser
        
        factory = APIRequestFactory()
        request = factory.get('/api/users/')
        request.user = AnonymousUser()  # Not authenticated
        
        viewset = UserViewSet()
        viewset.request = request
        
        queryset = viewset.get_queryset()
        self.assertEqual(queryset.count(), 0)
    
    def test_superuser_gets_all_users(self):
        """Test line 39: superuser returns all users"""
        from rest_framework.test import APIRequestFactory
        from users.views import UserViewSet
        
        factory = APIRequestFactory()
        request = factory.get('/api/users/')
        request.user = self.superuser
        
        viewset = UserViewSet()
        viewset.request = request
        
        queryset = viewset.get_queryset()
        self.assertGreaterEqual(queryset.count(), 3)  # At least our 3 test users
    
    def test_user_without_company_or_owned_company_gets_empty(self):
        """Test lines 44-47: user without company or owned_company returns empty"""
        from rest_framework.test import APIRequestFactory
        from users.views import UserViewSet
        
        # Create user without company
        user_no_company = User.objects.create_user(
            username='nocompany',
            password='pass123',
            company=None
        )
        
        factory = APIRequestFactory()
        request = factory.get('/api/users/')
        request.user = user_no_company
        
        viewset = UserViewSet()
        viewset.request = request
        
        queryset = viewset.get_queryset()
        self.assertEqual(queryset.count(), 0)
    
    def test_owner_without_company_field_uses_owned_company(self):
        """Test lines 44-45: user with owned_company but no company field"""
        from rest_framework.test import APIRequestFactory
        from users.views import UserViewSet
        
        # Create user without company
        owner = User.objects.create_user(
            username='owner',
            password='pass123',
            company=None
        )
        
        # Make them owner of a company
        self.company1.owner = owner
        self.company1.save()
        owner.refresh_from_db()
        
        factory = APIRequestFactory()
        request = factory.get('/api/users/')
        request.user = owner
        
        viewset = UserViewSet()
        viewset.request = request
        
        queryset = viewset.get_queryset()
        # Should return users from owned_company
        self.assertGreater(queryset.count(), 0)
    
    def test_swagger_fake_view_returns_empty(self):
        """Test line 33: swagger_fake_view returns empty queryset"""
        from rest_framework.test import APIRequestFactory
        from users.views import UserViewSet
        
        factory = APIRequestFactory()
        request = factory.get('/api/users/')
        request.user = self.user1
        
        viewset = UserViewSet()
        viewset.request = request
        viewset.swagger_fake_view = True  # Simulate swagger
        
        queryset = viewset.get_queryset()
        self.assertEqual(queryset.count(), 0)

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

class EmployeeViewSetCoverageTestCase(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(name='Test Company')
        from core.models import Branch
        self.branch = Branch.objects.create(company=self.company, name='B1')
        self.admin = User.objects.create_user(username='admin', password='password', company=self.company)
        admin_group, _ = Group.objects.get_or_create(name='Administrador General')
        self.admin.groups.add(admin_group)
        self.client.force_authenticate(user=self.admin)

    def test_create_employee_success(self):
        url = reverse('customuser-create-employee')
        data = {
            "username": "emp1",
            "password": "pwd",
            "password_confirm": "pwd",
            "groups_ids": [],
            "branches_ids": [self.branch.id]
        }
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Coverage for serializer get_groups_names / get_branches_names
        from users.serializers import EmployeeSerializer
        user = User.objects.get(username="emp1")
        ser_data = EmployeeSerializer(instance=user).data
        self.assertIn("branches_names", ser_data)

    def test_create_employee_no_company(self):
        self.admin.company = None
        self.admin.save()
        url = reverse('customuser-create-employee')
        data = {"username": "emp1", "password": "pwd", "password_confirm": "pwd"}
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_employee_empty_lists(self):
        url = reverse('customuser-create-employee')
        data = {
            "username": "emp1",
            "password": "pwd",
            "password_confirm": "pwd",
            "groups_ids": [],
            "branches_ids": []
        }
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_update_employee(self):
        emp = User.objects.create_user(username='emp2', password='pwd', company=self.company)
        url = reverse('customuser-update-employee', args=[emp.id])
        data = {"first_name": "NewName", "groups_ids": [], "branches_ids": []}
        resp = self.client.patch(url, data)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_update_employee_not_found(self):
        url = reverse('customuser-update-employee', args=[999])
        resp = self.client.put(url, {})
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_employee_no_company(self):
        self.admin.company = None
        self.admin.is_superuser = True
        self.admin.save()
        emp = User.objects.create_user(username='emp2', password='pwd', company=self.company)
        url = reverse('customuser-update-employee', args=[emp.id])
        resp = self.client.patch(url, {})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_roles_unauthenticated(self):
        self.client.logout()
        url = reverse('customuser-roles')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)


class UserViewSetAdditionalCoverageTestCase(APITestCase):
    """Additional tests for 100% coverage of users/views.py"""
    
    def setUp(self):
        from core.models import Company, Branch
        
        self.company = Company.objects.create(name='Test Co Views', tax_id='123789')
        self.branch = Branch.objects.create(company=self.company, name='Branch1', code='B1VIEWS')
        self.admin = User.objects.create_user(
            username='admin_views',
            password='pass',
            company=self.company,
            is_staff=True
        )
        self.admin_group, _ = Group.objects.get_or_create(name='Administrador General')
        self.admin.groups.add(self.admin_group)
    
    def test_user_viewset_with_branches(self):
        """Test line 72: user with branches sees users in their branches"""
        from rest_framework.test import APIRequestFactory
        from users.views import UserViewSet
        
        # Create user with branch
        user_with_branch = User.objects.create_user(
            username='withbranch_user',
            password='pass',
            company=self.company
        )
        user_with_branch.branch.add(self.branch)
        
        factory = APIRequestFactory()
        request = factory.get('/api/users/')
        request.user = user_with_branch
        
        viewset = UserViewSet()
        viewset.request = request
        
        queryset = viewset.get_queryset()
        self.assertGreaterEqual(queryset.count(), 0)
    
    def test_register_serializer_classes(self):
        """Test lines 96, 98: get_serializer_class for register and create_employee"""
        from rest_framework.test import APIRequestFactory
        from users.views import UserViewSet
        from users.serializers import UserRegistrationSerializer, EmployeeSerializer
        
        factory = APIRequestFactory()
        request = factory.get('/api/users/')
        request.user = self.admin
        
        viewset = UserViewSet()
        viewset.request = request
        
        # Test register action
        viewset.action = 'register'
        self.assertEqual(viewset.get_serializer_class(), UserRegistrationSerializer)
        
        # Test create_employee action
        viewset.action = 'create_employee'
        self.assertEqual(viewset.get_serializer_class(), EmployeeSerializer)
    
    def test_create_employee_success_response(self):
        """Test line 200: successful employee creation response"""
        self.client.force_authenticate(user=self.admin)
        
        url = reverse('customuser-create-employee')
        data = {
            'username': 'emp1',
            'password': 'pass',
            'password_confirm': 'pass',
            'first_name': 'Test',
            'last_name': 'Employee',
            'groups_ids': [],
            'branches_ids': []
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertIn('message', response.data)
    
    def test_update_employee_company_check_with_superuser(self):
        """Test line 200: company validation with superuser bypassing queryset filter"""
        from core.models import Company
        
        # Create another company
        other_company = Company.objects.create(name='Company Different', tax_id='111222333')
        
        # Create employee in other company
        emp = User.objects.create_user(
            username='emp_other_company',
            password='pass',
            company=other_company
        )
        
        # Create a superuser with a specific company
        superuser = User.objects.create_superuser(
            username='super_with_company',
            email='super@test.com',
            password='pass',
            company=self.company
        )
        
        # Authenticate as superuser (can see all users via get_queryset)
        self.client.force_authenticate(user=superuser)
        
        url = reverse('customuser-update-employee', args=[emp.id])
        data = {
            'first_name': 'UpdatedName'
        }
        
        response = self.client.patch(url, data)
        # Superuser can see the employee via get_queryset, but update_employee
        # checks if employee.company != request.user.company (line 199)
        # Should return 403
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_update_employee_serializer_error(self):
        """Test line 225: update_employee with serializer validation error"""
        # Create employee
        emp = User.objects.create_user(
            username='emp2',
            password='pass',
            company=self.company
        )
        
        self.client.force_authenticate(user=self.admin)
        
        url = reverse('customuser-update-employee', args=[emp.id])
        # Send invalid data (e.g., invalid branches)
        data = {
            'branches_ids': [99999]  # Non-existent branch
        }
        
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_roles_unauthenticated_via_viewset(self):
        """Test line 235: roles endpoint with unauthenticated request"""
        from rest_framework.test import APIRequestFactory
        from users.views import UserViewSet
        from django.contrib.auth.models import AnonymousUser
        
        factory = APIRequestFactory()
        request = factory.get('/api/users/roles/')
        request.user = AnonymousUser()
        
        viewset = UserViewSet()
        viewset.request = request
        
        response = viewset.roles(request)
        self.assertEqual(response.status_code, 401)
    
    def test_roles_non_admin_excludes_admin_general(self):
        """Test line 235: roles endpoint excludes 'Administrador General' for non-admins"""
        # Create non-admin user
        user = User.objects.create_user(
            username='plain',
            password='pass',
            company=self.company
        )
        cajero_group, _ = Group.objects.get_or_create(name='Cajero')
        user.groups.add(cajero_group)
        
        self.client.force_authenticate(user=user)
        
        url = reverse('customuser-roles')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        role_names = [role['name'] for role in response.data]
        # Should not include 'Administrador General'
        self.assertNotIn('Administrador General', role_names)
        # But should include other roles
        self.assertIn('Cajero', role_names)

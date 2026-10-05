"""
Tests for core views (Branch management).
"""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from core.models import Company, Branch

from utils.tests import TenantTestCase

User = get_user_model()


class BranchViewSetTestCase(TestCase):
    """Test cases for BranchViewSet."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        # Create a company
        self.company = Company.objects.create(
            name="Test Company",
            tax_id="12345678",
            is_active=True
        )
        
        # Get or create admin group
        self.admin_group, _ = Group.objects.get_or_create(name='Administrador General')
        
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin',
            password='testpass123',
            email='admin@test.com',
            company=self.company
        )
        self.admin_user.groups.add(self.admin_group)
        
        # Set admin as company owner
        self.company.owner = self.admin_user
        self.company.save()
        
        # Create a branch for testing
        self.branch = Branch.objects.create(
            company=self.company,
            name="Main Branch",
            code="MAIN001",
            address="123 Main St",
            is_active=True
        )
        
        # Create another company for isolation testing
        self.company2 = Company.objects.create(
            name="Other Company",
            tax_id="87654321",
            is_active=True
        )
        
        self.other_user = User.objects.create_user(
            username='other',
            password='testpass123',
            email='other@test.com',
            company=self.company2
        )
        
        self.branch2 = Branch.objects.create(
            company=self.company2,
            name="Other Branch",
            code="OTHER001",
            address="456 Other St",
            is_active=True
        )
    
    def test_list_branches_authenticated(self):
        """Test that authenticated users can list branches from their company only."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/branches/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Main Branch')
    
    def test_list_branches_multi_tenant_isolation(self):
        """Test that users cannot see branches from other companies."""
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get('/api/branches/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Other Branch')
    
    def test_create_branch_authenticated(self):
        """Test that authenticated users can create branches in their company."""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'name': 'New Branch',
            'code': 'NEW001',
            'address': '789 New St',
            'is_active': True
        }
        response = self.client.post('/api/branches/', data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Branch')
        self.assertEqual(response.data['company'], self.company.id)
        
        # Verify branch was created with correct company
        branch = Branch.objects.get(code='NEW001')
        self.assertEqual(branch.company, self.company)
    
    def test_create_branch_unauthenticated(self):
        """Test that unauthenticated users cannot create branches."""
        data = {
            'name': 'New Branch',
            'code': 'NEW001',
            'address': '789 New St',
            'is_active': True
        }
        response = self.client.post('/api/branches/', data)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_update_branch(self):
        """Test that users can update branches from their company."""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'name': 'Updated Branch',
            'code': 'MAIN001',
            'address': '123 Main St Updated',
            'is_active': True
        }
        response = self.client.put(f'/api/branches/{self.branch.id}/', data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Branch')
        
        # Verify company hasn't changed
        self.branch.refresh_from_db()
        self.assertEqual(self.branch.company, self.company)
    
    def test_delete_branch(self):
        """Test that users can delete branches from their company."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(f'/api/branches/{self.branch.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Branch.objects.filter(id=self.branch.id).exists())
    
    def test_cannot_access_other_company_branch(self):
        """Test that users cannot access branches from other companies."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(f'/api/branches/{self.branch2.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class CoreViewSetCoverageTestCase(TenantTestCase, APITestCase):
    def setUp(self):
        super().setUp()
        self.client.force_authenticate(user=self.user)

    def test_branch_viewset_filters(self):
        response = self.client.get(reverse('branch-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_branch_viewset_swagger_fake_view(self):
        """Test line 33: swagger_fake_view returns empty queryset"""
        from rest_framework.test import APIRequestFactory
        from core.views import BranchViewSet
        
        factory = APIRequestFactory()
        request = factory.get('/api/branches/')
        request.user = self.user
        
        viewset = BranchViewSet()
        viewset.request = request
        viewset.swagger_fake_view = True  # Simulate swagger
        
        queryset = viewset.get_queryset()
        self.assertEqual(queryset.count(), 0)
    
    def test_branch_viewset_unauthenticated(self):
        """Test line 36: unauthenticated user returns empty queryset"""
        from rest_framework.test import APIRequestFactory
        from core.views import BranchViewSet
        from django.contrib.auth.models import AnonymousUser
        
        factory = APIRequestFactory()
        request = factory.get('/api/branches/')
        request.user = AnonymousUser()  # Not authenticated
        
        viewset = BranchViewSet()
        viewset.request = request
        
        queryset = viewset.get_queryset()
        self.assertEqual(queryset.count(), 0)
    
    def test_branch_viewset_superuser(self):
        """Test line 40: superuser sees all branches"""
        from rest_framework.test import APIRequestFactory
        from core.views import BranchViewSet
        
        # Create superuser
        superuser = User.objects.create_superuser(
            username='super_core',
            password='pass',
            email='super_core@test.com'
        )
        
        # Ensure there's at least one branch (from setUp or create new)
        if not Branch.objects.exists():
            Branch.objects.create(
                company=self.company,
                name='Test Branch Super',
                code='TBSUPER'
            )
        
        factory = APIRequestFactory()
        request = factory.get('/api/branches/')
        request.user = superuser
        
        viewset = BranchViewSet()
        viewset.request = request
        
        queryset = viewset.get_queryset()
        # Superuser should see all branches
        self.assertGreaterEqual(queryset.count(), 1)
    
    def test_branch_viewset_user_no_company(self):
        """Test line 46: user without company returns empty queryset"""
        from rest_framework.test import APIRequestFactory
        from core.views import BranchViewSet
        
        # Create user without company
        user_no_company = User.objects.create_user(
            username='nocompany',
            password='pass',
            company=None
        )
        
        factory = APIRequestFactory()
        request = factory.get('/api/branches/')
        request.user = user_no_company
        
        viewset = BranchViewSet()
        viewset.request = request
        
        queryset = viewset.get_queryset()
        self.assertEqual(queryset.count(), 0)
    
    def test_perform_create_no_company(self):
        """Test line 65: ValidationError when user has no company"""
        from rest_framework import serializers
        
        # Create user without company
        user_no_company = User.objects.create_user(
            username='nocompany2',
            password='pass',
            company=None
        )
        
        self.client.force_authenticate(user=user_no_company)
        
        data = {
            'name': 'Test Branch',
            'code': 'TEST001',
            'address': '123 Test St',
            'is_active': True
        }
        
        response = self.client.post('/api/branches/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('company', str(response.data))

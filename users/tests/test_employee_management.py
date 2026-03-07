"""
Tests for employee management functionality.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework.test import APIClient
from rest_framework import status
from core.models import Company, Branch

User = get_user_model()


class EmployeeManagementTestCase(TestCase):
    """Test cases for employee creation and management."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        # Get or create default groups/roles (created by migration)
        self.admin_group, _ = Group.objects.get_or_create(name='Administrador General')
        self.manager_group, _ = Group.objects.get_or_create(name='Gerente')
        self.cashier_group, _ = Group.objects.get_or_create(name='Cajero')
        
        # Create a company
        self.company = Company.objects.create(
            name="Test Company",
            tax_id="12345678",
            is_active=True
        )
        
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
        
        # Create branches
        self.branch1 = Branch.objects.create(
            company=self.company,
            name="Branch 1",
            code="BR001",
            is_active=True
        )
        
        self.branch2 = Branch.objects.create(
            company=self.company,
            name="Branch 2",
            code="BR002",
            is_active=True
        )
        
        # Create manager user
        self.manager_user = User.objects.create_user(
            username='manager',
            password='testpass123',
            email='manager@test.com',
            company=self.company
        )
        self.manager_user.groups.add(self.manager_group)
        
        # Create regular user (no admin privileges)
        self.regular_user = User.objects.create_user(
            username='regular',
            password='testpass123',
            email='regular@test.com',
            company=self.company
        )
        self.regular_user.groups.add(self.cashier_group)
    
    def test_admin_can_create_employee(self):
        """Test that admin users can create employees."""
        self.client.force_authenticate(user=self.admin_user)
        
        data = {
            'username': 'newemployee',
            'email': 'newemployee@test.com',
            'first_name': 'New',
            'last_name': 'Employee',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'groups_ids': [self.cashier_group.id],
            'branches_ids': [self.branch1.id]
        }
        
        response = self.client.post('/api/users/employees/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], 'newemployee')
        self.assertIn('Cajero', response.data['groups'])
        self.assertIn('Branch 1', response.data['branches'])
        
        # Verify employee was created with correct company
        employee = User.objects.get(username='newemployee')
        self.assertEqual(employee.company, self.company)
        self.assertTrue(employee.groups.filter(name='Cajero').exists())
        self.assertTrue(employee.branch.filter(name='Branch 1').exists())
    
    def test_manager_can_create_employee(self):
        """Test that manager users can create employees."""
        self.client.force_authenticate(user=self.manager_user)
        
        data = {
            'username': 'employee2',
            'email': 'employee2@test.com',
            'first_name': 'Second',
            'last_name': 'Employee',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'groups_ids': [self.cashier_group.id],
            'branches_ids': [self.branch2.id]
        }
        
        response = self.client.post('/api/users/employees/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_regular_user_cannot_create_employee(self):
        """Test that regular users cannot create employees."""
        self.client.force_authenticate(user=self.regular_user)
        
        data = {
            'username': 'employee3',
            'email': 'employee3@test.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'groups_ids': [self.cashier_group.id]
        }
        
        response = self.client.post('/api/users/employees/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_unauthenticated_cannot_create_employee(self):
        """Test that unauthenticated users cannot create employees."""
        data = {
            'username': 'employee4',
            'email': 'employee4@test.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123'
        }
        
        response = self.client.post('/api/users/employees/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_password_mismatch_validation(self):
        """Test password confirmation validation."""
        self.client.force_authenticate(user=self.admin_user)
        
        data = {
            'username': 'employee5',
            'email': 'employee5@test.com',
            'password': 'testpass123',
            'password_confirm': 'different',
            'groups_ids': [self.cashier_group.id]
        }
        
        response = self.client.post('/api/users/employees/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)
    
    def test_invalid_group_ids(self):
        """Test validation of invalid group IDs."""
        self.client.force_authenticate(user=self.admin_user)
        
        data = {
            'username': 'employee6',
            'email': 'employee6@test.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'groups_ids': [9999]  # Non-existent group
        }
        
        response = self.client.post('/api/users/employees/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('groups_ids', response.data)
    
    def test_invalid_branch_ids(self):
        """Test validation of invalid branch IDs."""
        self.client.force_authenticate(user=self.admin_user)
        
        data = {
            'username': 'employee7',
            'email': 'employee7@test.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'branches_ids': [9999]  # Non-existent branch
        }
        
        response = self.client.post('/api/users/employees/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('branches_ids', response.data)
    
    def test_cannot_assign_branch_from_other_company(self):
        """Test that employees cannot be assigned to branches from other companies."""
        # Create another company
        other_company = Company.objects.create(
            name="Other Company",
            tax_id="87654321"
        )
        
        other_branch = Branch.objects.create(
            company=other_company,
            name="Other Branch",
            code="OTH001"
        )
        
        self.client.force_authenticate(user=self.admin_user)
        
        data = {
            'username': 'employee8',
            'email': 'employee8@test.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'branches_ids': [other_branch.id]
        }
        
        response = self.client.post('/api/users/employees/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('branches_ids', response.data)
    
    def test_update_employee(self):
        """Test updating employee information."""
        # Create an employee
        employee = User.objects.create_user(
            username='employee_to_update',
            password='testpass123',
            email='update@test.com',
            company=self.company
        )
        employee.groups.add(self.cashier_group)
        
        self.client.force_authenticate(user=self.admin_user)
        
        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'groups_ids': [self.manager_group.id],
            'branches_ids': [self.branch1.id, self.branch2.id]
        }
        
        response = self.client.patch(
            f'/api/users/{employee.id}/employee/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Updated')
        self.assertIn('Gerente', response.data['groups'])
        
        # Verify changes in database
        employee.refresh_from_db()
        self.assertEqual(employee.first_name, 'Updated')
        self.assertTrue(employee.groups.filter(name='Gerente').exists())
        self.assertEqual(employee.branch.count(), 2)
    
    def test_manager_cannot_assign_admin_role(self):
        """Test that managers cannot assign Administrador General role."""
        self.client.force_authenticate(user=self.manager_user)
        
        data = {
            'username': 'employee9',
            'email': 'employee9@test.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'groups_ids': [self.admin_group.id]
        }
        
        response = self.client.post('/api/users/employees/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('groups_ids', response.data)
    
    def test_admin_can_assign_admin_role(self):
        """Test that admins can assign Administrador General role."""
        self.client.force_authenticate(user=self.admin_user)
        
        data = {
            'username': 'newadmin',
            'email': 'newadmin@test.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'groups_ids': [self.admin_group.id]
        }
        
        response = self.client.post('/api/users/employees/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('Administrador General', response.data['groups'])


class UserRegistrationTestCase(TestCase):
    """Test cases for user registration with automatic role assignment."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        # Create admin group (should be created by migration)
        self.admin_group, _ = Group.objects.get_or_create(name='Administrador General')
    
    def test_register_user_gets_admin_role(self):
        """Test that newly registered users get Administrador General role."""
        data = {
            'username': 'newowner',
            'email': 'owner@test.com',
            'first_name': 'Company',
            'last_name': 'Owner',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'company_name': 'New Company',
            'company_tax_id': '11111111'
        }
        
        response = self.client.post('/api/users/register/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify user has admin role
        user = User.objects.get(username='newowner')
        self.assertTrue(user.groups.filter(name='Administrador General').exists())
        
        # Verify user is company owner
        self.assertEqual(user.company.owner, user)
        self.assertEqual(user.company.name, 'New Company')

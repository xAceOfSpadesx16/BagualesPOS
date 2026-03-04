from unittest.mock import patch
from django.test import TestCase, RequestFactory
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django_multitenant.utils import get_current_tenant, set_current_tenant
from rest_framework_simplejwt.exceptions import InvalidToken
from core.models import Company, Branch
from core.middleware import TenantMiddleware

User = get_user_model()


class CompanyModelTest(TestCase):
    """
    Test cases for the Company model
    """
    
    def setUp(self):
        """Set up test data"""
        self.company_data = {
            'name': 'Test Company',
            'tax_id': '12-3456789-0',
            'is_active': True
        }
    
    def test_create_company(self):
        """Test creating a company with valid data"""
        company = Company.objects.create(**self.company_data)
        self.assertEqual(company.name, 'Test Company')
        self.assertEqual(company.tax_id, '12-3456789-0')
        self.assertTrue(company.is_active)
        self.assertIsNotNone(company.created_at)
        self.assertIsNotNone(company.updated_at)
    
    def test_company_str(self):
        """Test string representation of company"""
        company = Company.objects.create(**self.company_data)
        self.assertEqual(str(company), 'Test Company')
    
    def test_company_without_tax_id(self):
        """Test creating a company without tax_id (optional field)"""
        company = Company.objects.create(
            name='Company Without Tax ID',
            is_active=True
        )
        self.assertEqual(company.name, 'Company Without Tax ID')
        self.assertIsNone(company.tax_id)
    
    def test_company_without_logo(self):
        """Test creating a company without logo (optional field)"""
        company = Company.objects.create(**self.company_data)
        self.assertFalse(company.logo)
    
    def test_company_is_active_default(self):
        """Test that is_active defaults to True"""
        company = Company.objects.create(name='Active Company')
        self.assertTrue(company.is_active)
    
    def test_company_ordering(self):
        """Test that companies are ordered by name"""
        Company.objects.create(name='Zebra Company')
        Company.objects.create(name='Alpha Company')
        Company.objects.create(name='Beta Company')
        
        companies = list(Company.objects.all())
        self.assertEqual(companies[0].name, 'Alpha Company')
        self.assertEqual(companies[1].name, 'Beta Company')
        self.assertEqual(companies[2].name, 'Zebra Company')


class BranchModelTest(TestCase):
    """
    Test cases for the Branch model
    """
    
    def setUp(self):
        """Set up test data"""
        self.company = Company.objects.create(
            name='Test Company',
            tax_id='12-3456789-0',
            is_active=True
        )
        
        self.branch_data = {
            'company': self.company,
            'name': 'Main Branch',
            'code': 'MAIN-001',
            'address': '123 Main Street',
            'is_active': True
        }
    
    def test_create_branch(self):
        """Test creating a branch with valid data"""
        branch = Branch.objects.create(**self.branch_data)
        self.assertEqual(branch.name, 'Main Branch')
        self.assertEqual(branch.code, 'MAIN-001')
        self.assertEqual(branch.company, self.company)
        self.assertEqual(branch.address, '123 Main Street')
        self.assertTrue(branch.is_active)
        self.assertIsNotNone(branch.created_at)
        self.assertIsNotNone(branch.updated_at)
    
    def test_branch_str(self):
        """Test string representation of branch"""
        branch = Branch.objects.create(**self.branch_data)
        self.assertEqual(str(branch), 'Test Company - Main Branch')
    
    def test_branch_requires_company(self):
        """Test that branch requires a company (CASCADE relationship)"""
        branch_data = self.branch_data.copy()
        branch_data.pop('company')
        
        with self.assertRaises(IntegrityError):
            Branch.objects.create(**branch_data)
    
    def test_branch_code_unique(self):
        """Test that branch code must be unique"""
        Branch.objects.create(**self.branch_data)
        
        # Try to create another branch with the same code
        branch_data_2 = self.branch_data.copy()
        branch_data_2['name'] = 'Secondary Branch'
        
        with self.assertRaises(IntegrityError):
            Branch.objects.create(**branch_data_2)
    
    def test_branch_without_address(self):
        """Test creating a branch without address (optional field)"""
        branch_data = self.branch_data.copy()
        branch_data.pop('address')
        branch = Branch.objects.create(**branch_data)
        self.assertIsNone(branch.address)
    
    def test_branch_is_active_default(self):
        """Test that is_active defaults to True"""
        branch = Branch.objects.create(
            company=self.company,
            name='Active Branch',
            code='ACT-001'
        )
        self.assertTrue(branch.is_active)
    
    def test_branch_ordering(self):
        """Test that branches are ordered by company and name"""
        company2 = Company.objects.create(name='Another Company')
        
        Branch.objects.create(company=self.company, name='Zebra Branch', code='Z001')
        Branch.objects.create(company=self.company, name='Alpha Branch', code='A001')
        Branch.objects.create(company=company2, name='Beta Branch', code='B001')
        
        branches = list(Branch.objects.all())
        # Should be ordered by company name first, then branch name
        self.assertEqual(branches[0].company, company2)  # "Another Company" comes first
        self.assertEqual(branches[1].name, 'Alpha Branch')  # "Test Company" branches
        self.assertEqual(branches[2].name, 'Zebra Branch')
    
    def test_company_deletion_cascades_to_branches(self):
        """Test that deleting a company deletes its branches"""
        branch = Branch.objects.create(**self.branch_data)
        branch_id = branch.id
        
        self.company.delete()
        
        # Branch should be deleted
        with self.assertRaises(Branch.DoesNotExist):
            Branch.objects.get(id=branch_id)
    
    def test_company_branches_relation(self):
        """Test the reverse relationship from company to branches"""
        branch1 = Branch.objects.create(
            company=self.company,
            name='Branch 1',
            code='BR-001'
        )
        branch2 = Branch.objects.create(
            company=self.company,
            name='Branch 2',
            code='BR-002'
        )
        
        branches = self.company.branches.all()
        self.assertEqual(branches.count(), 2)
        self.assertIn(branch1, branches)
        self.assertIn(branch2, branches)
    
    def test_branch_unique_together_company_code(self):
        """Test that company + code combination must be unique"""
        Branch.objects.create(**self.branch_data)
        
        # Create another company
        company2 = Company.objects.create(name='Another Company')
        
        # Same code but different company should work
        branch2_data = self.branch_data.copy()
        branch2_data['company'] = company2
        branch2_data['name'] = 'Another Branch'
        
        # This should work because it's a different company
        branch2 = Branch.objects.create(**branch2_data)
        self.assertEqual(branch2.code, 'MAIN-001')
        self.assertEqual(branch2.company, company2)


# ============================================================
# Tests consolidated from test_middleware_*.py, test_tenant_isolation.py, test_phase2_integration.py
# ============================================================
class MiddlewareTestCase(TestCase):
    """Middleware tests - consolidated from test_middleware_*.py"""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = TenantMiddleware(lambda r: None)
        
    def tearDown(self):
        set_current_tenant(None)
    
    def test_middleware_with_regular_user(self):
        """Test middleware with user that has company"""
        company = Company.objects.create(name="Test Co", tax_id="123")
        user = User.objects.create_user(username='regular', password='test', company=company)
        
        request = self.factory.get('/')
        request.user = user
        
        self.middleware.process_request(request)
        
        current_tenant = get_current_tenant()
        self.assertEqual(current_tenant, company)
    
    def test_middleware_with_unauthenticated_user(self):
        """Test middleware with unauthenticated user"""
        request = self.factory.get('/')
        request.user = AnonymousUser()
        
        self.middleware.process_request(request)
        
        current_tenant = get_current_tenant()
        self.assertIsNone(current_tenant)

    def test_middleware_with_invalid_jwt_token(self):
        """Test middleware when JWT authentication raises InvalidToken — covers except branch"""
        request = self.factory.get('/')
        request.user = AnonymousUser()
        request.META['HTTP_AUTHORIZATION'] = 'Bearer invalid.token.here'

        with patch(
            'core.middleware.JWTAuthentication.authenticate',
            side_effect=InvalidToken("Token is invalid")
        ):
            self.middleware.process_request(request)

        self.assertIsNone(get_current_tenant())

class TenantIsolationTestCase(TestCase):
    """Tenant isolation tests - consolidated from test_tenant_isolation.py and test_phase2_integration.py"""
    
    def setUp(self):
        self.company_a = Company.objects.create(name="Company A", tax_id="12345678A")
        self.user_a = User.objects.create_user(username="user_a", email="usera@example.com", password="password123", company=self.company_a)
        self.company_a.owner = self.user_a
        self.company_a.save()
        
        self.company_b = Company.objects.create(name="Company B", tax_id="87654321B")
        self.user_b = User.objects.create_user(username="user_b", email="userb@example.com", password="password123", company=self.company_b)
        self.company_b.owner = self.user_b
        self.company_b.save()
    
    def tearDown(self):
        set_current_tenant(None)
    
    def test_branch_isolation(self):
        """Test that branches are isolated per tenant"""
        set_current_tenant(self.company_a)
        branch_a1 = Branch.objects.create(company=self.company_a, name="Branch A1", code="A1", address="123 Main St")
        branch_a2 = Branch.objects.create(company=self.company_a, name="Branch A2", code="A2", address="456 Oak Ave")
        
        branches_a = Branch.objects.all()
        self.assertEqual(branches_a.count(), 2)
        
        set_current_tenant(self.company_b)
        branch_b1 = Branch.objects.create(company=self.company_b, name="Branch B1", code="B1", address="789 Elm St")
        
        branches_b = Branch.objects.all()
        self.assertEqual(branches_b.count(), 1)
        self.assertIn(branch_b1, branches_b)
        
        set_current_tenant(self.company_a)
        branches_a_again = Branch.objects.all()
        self.assertEqual(branches_a_again.count(), 2)
    
    def test_cross_tenant_prevention(self):
        """Test that cross-tenant data access is prevented"""
        set_current_tenant(self.company_a)
        branch_a = Branch.objects.create(company=self.company_a, name="Branch A", code="A", address="123 Main St")
        
        set_current_tenant(self.company_b)
        
        with self.assertRaises(Branch.DoesNotExist):
            Branch.objects.get(id=branch_a.id)
        
        all_branches = Branch.objects.all()
        self.assertEqual(all_branches.count(), 0)

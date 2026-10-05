"""
Test utilities for multi-tenant testing.
Provides helpers to create test objects with proper company context.
"""
from django.contrib.auth import get_user_model
from core.models import Company, Branch
from django_multitenant.utils import set_current_tenant

User = get_user_model()


class TenantTestCase:
    """
    Mixin for test cases that need multi-tenant support.
    Automatically creates a company and user for testing.
    """
    
    @classmethod
    def setUpTestData(cls):
        """Create default company and user for tests."""
        super().setUpTestData()
        
        # Create default company
        cls.company = Company.objects.create(
            name="Test Company",
            tax_id="12345678"
        )
        
        # Create default user
        cls.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            company=cls.company
        )
        
        # Set user as company owner
        cls.company.owner = cls.user
        cls.company.save()
        
        # Set tenant context
        set_current_tenant(cls.company)
    
    def setUp(self):
        """Ensure tenant context is set for each test."""
        super().setUp()
        set_current_tenant(self.company)
    
    def tearDown(self):
        """Clear tenant context after each test."""
        super().tearDown()
        set_current_tenant(None)


def create_test_company(name="Test Company", tax_id="12345678"):
    """Helper to create a test company."""
    return Company.objects.create(name=name, tax_id=tax_id)


def create_test_user(username="testuser", company=None, **kwargs):
    """Helper to create a test user with company."""
    if company is None:
        company = create_test_company()
    
    user = User.objects.create_user(
        username=username,
        email=kwargs.get('email', f'{username}@example.com'),
        password=kwargs.get('password', 'testpass123'),
        company=company,
        **{k: v for k, v in kwargs.items() if k not in ['email', 'password']}
    )
    
    # Set as owner if company doesn't have one
    if not company.owner:
        company.owner = user
        company.save()
    
    return user


def create_test_branch(company=None, name="Test Branch", code="TB01"):
    """Helper to create a test branch."""
    if company is None:
        company = create_test_company()
    
    return Branch.objects.create(
        company=company,
        name=name,
        code=code
    )

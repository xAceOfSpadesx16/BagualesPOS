from django.test import TestCase
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model

from users.admin import CustomUserAdmin
from core.models import Company, Branch

User = get_user_model()


class CustomUserAdminTest(TestCase):
    """
    Test cases for CustomUserAdmin
    """
    
    def setUp(self):
        """Set up test data"""
        self.site = AdminSite()
        self.admin = CustomUserAdmin(User, self.site)
        
        # Create company and branch
        self.company = Company.objects.create(
            name='Test Company',
            is_active=True
        )
        
        self.branch = Branch.objects.create(
            company=self.company,
            name='Test Branch',
            code='TEST-001',
            is_active=True
        )
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.user.branch.add(self.branch)
    
    def test_get_queryset_prefetches_branches(self):
        """Test that get_queryset uses prefetch_related for branches"""
        from django.test import RequestFactory
        
        request = RequestFactory().get('/admin/users/customuser/')
        request.user = self.user
        
        queryset = self.admin.get_queryset(request)
        
        # Check that queryset is optimized with prefetch_related
        # We can verify this by checking _prefetch_related_lookups
        self.assertIn('branch', queryset._prefetch_related_lookups)
    
    def test_fieldsets_includes_branch_assignment(self):
        """Test that fieldsets includes branch assignment section"""
        fieldsets = self.admin.fieldsets
        
        # Find the branch assignment fieldset
        branch_fieldset = None
        for name, options in fieldsets:
            if name == 'Branch Assignment':
                branch_fieldset = options
                break
        
        self.assertIsNotNone(branch_fieldset)
        self.assertIn('branch', branch_fieldset['fields'])
    
    def test_filter_horizontal_includes_branch(self):
        """Test that filter_horizontal includes branch field"""
        self.assertIn('branch', self.admin.filter_horizontal)
    
    def test_list_filter_includes_branch(self):
        """Test that list_filter includes branch field"""
        self.assertIn('branch', self.admin.list_filter)

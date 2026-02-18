from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal

from sales.models import Sale, PayMethod
from cash.models import CashSession
from devices.models import CashRegister
from core.models import Company, Branch

User = get_user_model()


class SaleBranchIntegrationTest(TestCase):
    """
    Test cases for Sale branch auto-population from cash session
    """
    
    def setUp(self):
        """Set up test data"""
        # Create company and branches
        self.company = Company.objects.create(
            name='Test Company',
            is_active=True
        )
        
        self.branch_a = Branch.objects.create(
            company=self.company,
            name='Branch A',
            code='BR-A',
            is_active=True
        )
        
        self.branch_b = Branch.objects.create(
            company=self.company,
            name='Branch B',
            code='BR-B',
            is_active=True
        )
        
        # Create users
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        
        # Create cash registers with branches
        self.register_a = CashRegister.objects.create(
            name='Register A',
            code='REG-A-001',
            branch=self.branch_a
        )
        
        self.register_b = CashRegister.objects.create(
            name='Register B',
            code='REG-B-001',
            branch=self.branch_b
        )
        
        # Create cash session
        self.session_a = CashSession.objects.create(
            cash_register=self.register_a,
            user=self.user,
            opening_balance=Decimal('1000.00')
        )
        
        self.session_b = CashSession.objects.create(
            cash_register=self.register_b,
            user=self.user,
            opening_balance=Decimal('1000.00')
        )
    
    def test_sale_branch_auto_populated_from_session(self):
        """Test that sale branch is auto-populated from cash_session"""
        sale = Sale.objects.create(
            seller=self.user,
            cash_session=self.session_a,
            total_amount=Decimal('100.00')
        )
        
        # Refresh from database
        sale.refresh_from_db()
        
        # Branch should be auto-populated from session's register
        self.assertEqual(sale.branch, self.branch_a)
    
    def test_sale_branch_different_sessions(self):
        """Test that different sessions populate different branches"""
        sale_a = Sale.objects.create(
            seller=self.user,
            cash_session=self.session_a,
            total_amount=Decimal('100.00')
        )
        
        sale_b = Sale.objects.create(
            seller=self.user,
            cash_session=self.session_b,
            total_amount=Decimal('200.00')
        )
        
        # Refresh from database
        sale_a.refresh_from_db()
        sale_b.refresh_from_db()
        
        # Each sale should have the correct branch
        self.assertEqual(sale_a.branch, self.branch_a)
        self.assertEqual(sale_b.branch, self.branch_b)
    
    def test_sale_branch_not_overwritten_if_set(self):
        """Test that manually set branch is not overwritten"""
        sale = Sale.objects.create(
            seller=self.user,
            cash_session=self.session_a,
            branch=self.branch_b,  # Manually set to branch B
            total_amount=Decimal('100.00')
        )
        
        # Refresh from database
        sale.refresh_from_db()
        
        # Branch should remain as manually set (branch B)
        self.assertEqual(sale.branch, self.branch_b)
    
    def test_sale_without_session_no_branch(self):
        """Test that sale without session has no auto-populated branch"""
        sale = Sale.objects.create(
            seller=self.user,
            total_amount=Decimal('100.00')
        )
        
        # Refresh from database
        sale.refresh_from_db()
        
        # Branch should be None
        self.assertIsNone(sale.branch)
    
    def test_sale_branch_persists_after_session_deletion(self):
        """Test that branch remains even if session is deleted (SET_NULL)"""
        sale = Sale.objects.create(
            seller=self.user,
            cash_session=self.session_a,
            total_amount=Decimal('100.00')
        )
        
        # Refresh and verify branch is set
        sale.refresh_from_db()
        self.assertEqual(sale.branch, self.branch_a)
        
        # Delete the session
        self.session_a.delete()
        
        # Refresh sale
        sale.refresh_from_db()
        
        # Session should be None but branch should remain
        self.assertIsNone(sale.cash_session)
        self.assertEqual(sale.branch, self.branch_a)
    
    def test_sale_branch_persists_after_register_deletion(self):
        """Test that branch remains even if register is deleted"""
        sale = Sale.objects.create(
            seller=self.user,
            cash_session=self.session_a,
            total_amount=Decimal('100.00')
        )
        
        # Refresh and verify branch is set
        sale.refresh_from_db()
        self.assertEqual(sale.branch, self.branch_a)
        
        # Store branch reference
        branch_ref = sale.branch
        
        # Delete the register (this will delete session due to PROTECT, so we need to delete session first)
        self.session_a.delete()
        self.register_a.delete()
        
        # Refresh sale
        sale.refresh_from_db()
        
        # Branch should still be set (SET_NULL on branch FK)
        self.assertEqual(sale.branch, branch_ref)
    
    def test_sale_branch_null_after_branch_deletion(self):
        """Test that sale branch is null after branch is deleted (SET_NULL)"""
        sale = Sale.objects.create(
            seller=self.user,
            cash_session=self.session_a,
            total_amount=Decimal('100.00')
        )
        
        # Refresh and verify branch is set
        sale.refresh_from_db()
        self.assertEqual(sale.branch, self.branch_a)
        
        # Delete sessions and register first (to avoid PROTECT constraint)
        self.session_a.delete()
        self.register_a.delete()
        
        # Delete the branch
        self.branch_a.delete()
        
        # Refresh sale
        sale.refresh_from_db()
        
        # Branch should be None due to SET_NULL
        self.assertIsNone(sale.branch)
    
    def test_sale_update_preserves_branch(self):
        """Test that updating a sale preserves the branch"""
        sale = Sale.objects.create(
            seller=self.user,
            cash_session=self.session_a,
            total_amount=Decimal('100.00')
        )
        
        # Refresh and verify branch is set
        sale.refresh_from_db()
        self.assertEqual(sale.branch, self.branch_a)
        
        # Update the sale
        sale.total_amount = Decimal('200.00')
        sale.save()
        
        # Refresh and verify branch is still set
        sale.refresh_from_db()
        self.assertEqual(sale.branch, self.branch_a)

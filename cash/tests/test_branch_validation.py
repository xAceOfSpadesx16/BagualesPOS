from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from decimal import Decimal

from cash.models import CashSession
from devices.models import CashRegister
from core.models import Company, Branch

User = get_user_model()


class CashSessionBranchValidationTest(TestCase):
    """
    Test cases for CashSession branch access validation
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
        self.user_branch_a = User.objects.create_user(
            username='user_a',
            password='testpass123',
            email='usera@example.com'
        )
        self.user_branch_a.branch.add(self.branch_a)
        
        self.user_branch_b = User.objects.create_user(
            username='user_b',
            password='testpass123',
            email='userb@example.com'
        )
        self.user_branch_b.branch.add(self.branch_b)
        
        self.user_global = User.objects.create_user(
            username='user_global',
            password='testpass123',
            email='global@example.com'
        )
        # No branch assignment - global user
        
        self.user_both = User.objects.create_user(
            username='user_both',
            password='testpass123',
            email='both@example.com'
        )
        self.user_both.branch.add(self.branch_a, self.branch_b)
        
        # Create cash registers
        self.register_a = CashRegister.objects.create(
            name='Register A',
            code='REG-BV-A-001',
            branch=self.branch_a
        )
        
        self.register_b = CashRegister.objects.create(
            name='Register B',
            code='REG-BV-B-001',
            branch=self.branch_b
        )
        
        self.register_no_branch = CashRegister.objects.create(
            name='Register No Branch',
            code='REG-BV-NONE-001'
        )
    
    def test_user_can_open_session_in_assigned_branch(self):
        """Test that user assigned to branch A can open session in branch A"""
        session = CashSession(
            cash_register=self.register_a,
            user=self.user_branch_a,
            opening_balance=Decimal('1000.00')
        )
        
        # Should not raise ValidationError
        try:
            session.full_clean()
            session.save()
        except ValidationError:
            self.fail("User should be able to open session in assigned branch")
        
        self.assertIsNotNone(session.pk)
    
    def test_user_cannot_open_session_in_unassigned_branch(self):
        """Test that user assigned to branch A cannot open session in branch B"""
        session = CashSession(
            cash_register=self.register_b,
            user=self.user_branch_a,
            opening_balance=Decimal('1000.00')
        )
        
        # Should raise ValidationError
        with self.assertRaises(ValidationError) as context:
            session.full_clean()
        
        self.assertIn('user', context.exception.error_dict)
        self.assertIn('does not have access', str(context.exception))
    
    def test_global_user_can_open_session_anywhere(self):
        """Test that user without branch assignments can open session anywhere"""
        # Test session in branch A
        session_a = CashSession(
            cash_register=self.register_a,
            user=self.user_global,
            opening_balance=Decimal('1000.00')
        )
        
        # Should not raise ValidationError
        try:
            session_a.full_clean()
            session_a.save()
        except ValidationError:
            self.fail("Global user should be able to open sessions in any branch")
        
        self.assertIsNotNone(session_a.pk)
        
        # Close session A before opening session B (only one session per user)
        from cash.choices import SessionStatus
        session_a.status = SessionStatus.CLOSED
        session_a.closing_balance = Decimal('1000.00')
        from django.utils import timezone
        session_a.closing_date = timezone.now()
        session_a.save()
        
        # Test session in branch B
        session_b = CashSession(
            cash_register=self.register_b,
            user=self.user_global,
            opening_balance=Decimal('2000.00')
        )
        
        try:
            session_b.full_clean()
            session_b.save()
        except ValidationError:
            self.fail("Global user should be able to open sessions in any branch")
        
        self.assertIsNotNone(session_b.pk)
    
    def test_user_with_multiple_branches_can_access_all(self):
        """Test that user assigned to multiple branches can access all of them"""
        # Test session in branch A
        session_a = CashSession(
            cash_register=self.register_a,
            user=self.user_both,
            opening_balance=Decimal('1000.00')
        )
        
        # Should not raise ValidationError
        try:
            session_a.full_clean()
            session_a.save()
        except ValidationError:
            self.fail("User with multiple branches should access all assigned branches")
        
        self.assertIsNotNone(session_a.pk)
        
        # Close session A before opening session B (only one session per user)
        from cash.choices import SessionStatus
        session_a.status = SessionStatus.CLOSED
        session_a.closing_balance = Decimal('1000.00')
        from django.utils import timezone
        session_a.closing_date = timezone.now()
        session_a.save()
        
        # Test session in branch B
        session_b = CashSession(
            cash_register=self.register_b,
            user=self.user_both,
            opening_balance=Decimal('2000.00')
        )
        
        try:
            session_b.full_clean()
            session_b.save()
        except ValidationError:
            self.fail("User with multiple branches should access all assigned branches")
        
        self.assertIsNotNone(session_b.pk)
    
    def test_any_user_can_use_register_without_branch(self):
        """Test that any user can use a register without branch assignment"""
        # Test with user assigned to branch A
        session_a = CashSession(
            cash_register=self.register_no_branch,
            user=self.user_branch_a,
            opening_balance=Decimal('1000.00')
        )
        
        # Should not raise ValidationError
        try:
            session_a.full_clean()
            session_a.save()
        except ValidationError:
            self.fail("Any user should be able to use register without branch")
        
        self.assertIsNotNone(session_a.pk)
        
        # Close session before opening another one (only one session per register)
        from cash.choices import SessionStatus
        session_a.status = SessionStatus.CLOSED
        session_a.closing_balance = Decimal('1000.00')
        from django.utils import timezone
        session_a.closing_date = timezone.now()
        session_a.save()
        
        # Test with global user
        session_global = CashSession(
            cash_register=self.register_no_branch,
            user=self.user_global,
            opening_balance=Decimal('2000.00')
        )
        
        try:
            session_global.full_clean()
            session_global.save()
        except ValidationError:
            self.fail("Any user should be able to use register without branch")
        
        self.assertIsNotNone(session_global.pk)
    
    def test_validation_message_includes_user_branches(self):
        """Test that validation error message includes user's assigned branches"""
        session = CashSession(
            cash_register=self.register_b,
            user=self.user_branch_a,
            opening_balance=Decimal('1000.00')
        )
        
        with self.assertRaises(ValidationError) as context:
            session.full_clean()
        
        error_message = str(context.exception)
        self.assertIn('Branch A', error_message)
    
    def test_validation_only_on_new_sessions(self):
        """Test that branch validation is applied correctly on new sessions"""
        # Create a valid session first
        session = CashSession.objects.create(
            cash_register=self.register_a,
            user=self.user_branch_a,
            opening_balance=Decimal('1000.00')
        )
        
        # Updating the session should work
        session.opening_balance = Decimal('1500.00')
        try:
            session.full_clean()
            session.save()
        except ValidationError:
            self.fail("Updating existing session should not trigger branch validation issues")

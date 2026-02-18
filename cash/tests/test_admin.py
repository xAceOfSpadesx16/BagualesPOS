from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.admin.sites import AdminSite

from devices.models import CashRegister
from cash.models import CashSession
from cash.choices import SessionStatus
from cash.admin import CashSessionAdmin

User = get_user_model()


class AdminTestCase(TestCase):
    """Tests for admin functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='admintest',
            password='test',
            first_name='Admin',
            last_name='Test'
        )
        self.cash_register = CashRegister.objects.create(
            code='ADMIN-01',
            name='Admin Test Register',
            is_active=True
        )

    def test_admin_difference_method(self):
        """Test admin difference method formatting"""
        
        admin_instance = CashSessionAdmin(CashSession, AdminSite())
        
        # Create session with positive difference
        session_positive = CashSession.objects.create(
            cash_register=self.cash_register,
            user=self.user,
            opening_balance=Decimal('1000.00'),
            closing_balance=Decimal('1200.00'),
            status=SessionStatus.CLOSED,
            closing_date=timezone.now()
        )
        
        # Test positive difference (should have + prefix)
        diff_str = admin_instance.difference(session_positive)
        self.assertTrue(diff_str.startswith('+'))
        
        # Create session with negative difference  
        session_negative = CashSession.objects.create(
            cash_register=self.cash_register,
            user=self.user,
            opening_balance=Decimal('1000.00'),
            closing_balance=Decimal('800.00'),
            status=SessionStatus.CLOSED,
            closing_date=timezone.now()
        )
        
        # Test negative difference
        diff_str = admin_instance.difference(session_negative)
        self.assertFalse(diff_str.startswith('+'))
        self.assertIn('-', diff_str)

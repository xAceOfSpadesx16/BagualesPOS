from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model

from sales.models import Sale
from clients.models import Client
from devices.models import CashRegister
from cash.models import CashSession
from cash.choices import SessionStatus

User = get_user_model()


class ManagerTests(TestCase):
    """Tests for manager methods"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='mgr', password='test')
        cr = CashRegister.objects.create(code='M1', name='M1', is_active=True)
        self.session = CashSession.objects.create(
            cash_register=cr, user=self.user,
            opening_balance=Decimal('1000'), status=SessionStatus.OPEN
        )
        
    def test_manager_methods(self):
        """Test all manager queryset methods"""
        # Create sale
        sale = Sale.objects.create(seller=self.user, cash_session=self.session)
        
        # select_rel_seller - access via get_queryset()
        qs = Sale.objects.get_queryset()
        result = qs.select_rel_seller().first()
        self.assertIsNotNone(result)
        
        # select_rel_client
        client = Client.objects.create(name='T', last_name='U', dni='1')
        sale.client = client
        sale.save()
        qs = Sale.objects.get_queryset()
        result = qs.select_rel_client().first()
        self.assertIsNotNone(result)
        
        # prefetch_details_products
        qs = Sale.objects.get_queryset()
        result = qs.prefetch_details_products().first()
        self.assertIsNotNone(result)
        
        # get_own_actives
        qs = Sale.objects.get_queryset()
        result_qs = qs.get_own_actives(self.user)
        self.assertEqual(result_qs.count(), 1)
        
        # get_table_active_sale (manager method)
        result = Sale.objects.get_table_active_sale(self.user)
        self.assertIsNotNone(result)
        
        # fetch_details (manager method)
        qs = Sale.objects.fetch_details()
        self.assertIsNotNone(qs.first())

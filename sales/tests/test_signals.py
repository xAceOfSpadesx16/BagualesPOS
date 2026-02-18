from decimal import Decimal
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from sales.models import Sale, SaleDetail
from products.models import Product, Category, Brand, Season, Color, Gender
from inventory.models import Inventory
from clients.models import Client, CustomerAccount, CustomerBalanceRecord
from devices.models import CashRegister
from cash.models import CashSession
from cash.choices import SessionStatus

User = get_user_model()

class SignalsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='signal_test', password='test')
        
        # Setup Cash Session
        cr = CashRegister.objects.create(code='S1', name='S1', is_active=True)
        self.session = CashSession.objects.create(
            cash_register=cr,
            user=self.user,
            opening_balance=Decimal('1000'),
            status=SessionStatus.OPEN
        )
        
        # Setup Product
        cat = Category.objects.create(name='SigCat')
        br = Brand.objects.create(name='SigBr')
        se = Season.objects.create(name='SigSe')
        co = Color.objects.create(name='SigCo', code='#FFF')
        ge = Gender.objects.create(name='SigGe')
        
        self.prod = Product.objects.create(
            name='SigProd', category=cat, brand=br, season=se,
            color=co, gender=ge, sale_price=Decimal('100'), cost_price=Decimal('50')
        )
        self.inventory = Inventory.objects.get(product=self.prod)
        self.inventory.quantity = 100
        self.inventory.save()
        self.prod.refresh_from_db()

    def test_update_stock_no_inventory(self):
        """Test signal when product has no inventory"""
        # Create product without inventory
        try:
            self.prod.inventory.delete()
        except:
            pass
            
        # Refresh prod to clear likely cached relation
        self.prod.refresh_from_db()
        
        sale = Sale.objects.create(seller=self.user, cash_session=self.session)
        
        # Create detail - should trigger signal and raise ValidationError because no inventory
        with self.assertRaisesMessage(ValidationError, 'does not have inventory'):
            SaleDetail.objects.create(
                order=sale,
                product=self.prod,
                quantity=1,
                sale_price=Decimal('10'),
                cost_price=Decimal('5')
            )

    def test_update_stock_negative_prevention(self):
        """Test signal preventing negative stock"""
        # Set stock to 5
        self.inventory.quantity = 5
        self.inventory.save()
        
        sale = Sale.objects.create(seller=self.user, cash_session=self.session)
        
        # Try to sell 10. clean() prevents this usually, but we want to hit the signal check.
        # We can construct the object and call save() bypassing full_clean()
        detail = SaleDetail(
            order=sale,
            product=self.prod,
            quantity=10,
            sale_price=Decimal('10'),
            cost_price=Decimal('5')
        )
        
        # Signal runs on save
        with self.assertRaisesMessage(ValidationError, 'Stock would become negative'):
            detail.save()

    def test_restore_stock_on_delete(self):
        """Test stock restoration on SaleDetail delete"""
        
        sale = Sale.objects.create(seller=self.user, cash_session=self.session)
        detail = SaleDetail.objects.create(
            order=sale,
            product=self.prod,
            quantity=5,
            sale_price=Decimal('10'),
            cost_price=Decimal('5')
        )
        
        # Stock should be 95
        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.quantity, 95)
        
        # Delete detail
        # Re-fetch to ensure no stale product/inventory cache is attached
        detail = SaleDetail.objects.get(pk=detail.pk)
        detail.delete()
        
        # Stock should be 100
        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.quantity, 100)

    def test_accounting_no_customer_account(self):
        """Test integration when client has no customer account"""
        client = Client.objects.create(
            name='NoAccount', 
            last_name='Client', 
            dni='111', 
            approved_customer_account=False # Should prevent auto-creation if logic exists logic
        )
        # Ensure no account exists (delete if auto-created)
        if hasattr(client, 'customer_account'):
            client.customer_account.delete()
            client.refresh_from_db()
            
        sale = Sale.objects.create(
            seller=self.user,
            cash_session=self.session,
            client=client,
            closed=False
        )
        
        # Close sale
        sale.closed = True
        sale.save()
        
        # Assert no errors and no balance record logic (implied by success)
        
    def test_accounting_inactive_account(self):
        """Test integration when customer account is inactive"""
        client = Client.objects.create(name='Inactive', last_name='Client', dni='222')
        # Account auto-created usually
        account = client.customer_account
        account.active = False
        account.save()
        
        sale = Sale.objects.create(
            seller=self.user,
            cash_session=self.session,
            client=client,
            closed=False
        )
        
        # Close sale
        sale.closed = True
        sale.save()
        
        # Assert no balance record created
        self.assertFalse(CustomerBalanceRecord.objects.filter(sale=sale).exists())

    def test_accounting_avoid_duplicate(self):
        """Test integration avoids duplicate records"""
        from clients.choices import MovementType
        
        client = Client.objects.create(name='Dupe', last_name='Client', dni='333')
        account = client.customer_account
        
        sale = Sale.objects.create(
            seller=self.user,
            cash_session=self.session,
            client=client,
            closed=False
        )
        
        # Manually create a balance record to simulate "already processed"
        existing_record = CustomerBalanceRecord.objects.create(
            customer_account=account,
            sale=sale,
            amount=Decimal('100.00'),
            movement_type=MovementType.DEBIT,
            notes='Existing record',
            created_by=self.user
        )
        
        # Set the account_record to simulate already processed
        sale.account_record = existing_record
        sale.save()
        
        # Close sale
        sale.closed = True
        sale.save()
        
        # Assert no additional balance record created (should still be 1)
        self.assertEqual(CustomerBalanceRecord.objects.filter(sale=sale).count(), 1)
        self.assertEqual(CustomerBalanceRecord.objects.filter(sale=sale).first().id, existing_record.id)

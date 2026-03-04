from decimal import Decimal
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from utils.tests import TenantTestCase, create_test_branch

from sales.models import Sale, SaleDetail, PayMethod
from clients.models import Client
from products.models import Product, Category, Brand, Season, Color, Gender
from devices.models import CashRegister
from cash.models import CashSession
from cash.choices import SessionStatus
from inventory.models import Inventory

User = get_user_model()


class PayMethodModelTestCase(TenantTestCase, TestCase):
    """Test PayMethod model"""
    
    def test_paymethod_str(self):
        """Test PayMethod __str__ method"""
        pay_method = PayMethod.objects.create(company=self.company, name='Tarjeta de Crédito')
        self.assertEqual(str(pay_method), 'Tarjeta de Crédito')


class SaleModelTestCase(TenantTestCase, TestCase):
    """Test Sale model __str__ and validations"""
    
    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(
            username='testmodel',
            password='test',
            first_name='John',
            last_name='Doe'
        )
        self.client_obj = Client.objects.create(company=self.company, name='TestClient', last_name='Model', dni='456')
        self.branch = create_test_branch(company=self.company, code="TB1")
        
        cash_register = CashRegister.objects.create(company=self.company, 
            branch=self.branch,
            code='TEST-MODEL-01',
            name='Model Test Register',
            is_active=True
        )
        self.cash_session = CashSession.objects.create(company=self.company, 
            cash_register=cash_register,
            user=self.user,
            opening_balance=Decimal('1000.00'),
            status=SessionStatus.OPEN
        )
        
        self.pay_method = PayMethod.objects.create(company=self.company, name='Efectivo')
    
    def test_sale_str_with_client(self):
        """Test Sale __str__ with client"""
        sale = Sale.objects.create(company=self.company, 
            seller=self.user,
            client=self.client_obj,
            cash_session=self.cash_session
        )
        str_repr = str(sale)
        self.assertIn('TestClient', str_repr)
        self.assertIn('John Doe', str_repr)
    
    def test_sale_clean_closed_requires_cash_session(self):
        """Test that closed sales require cash_session"""
        sale = Sale.objects.create(company=self.company, seller=self.user)
        sale.closed = True
        sale.cash_session = None  # No cash session
        
        with self.assertRaises(ValidationError) as context:
            sale.full_clean()
        self.assertIn('cash_session', context.exception.message_dict)
    
    def test_sale_clean_closed_requires_pay_method(self):
        """Test that closed sales require pay_method"""
        sale = Sale.objects.create(company=self.company, seller=self.user, cash_session=self.cash_session)
        sale.closed = True
        sale.pay_method = None
        
        with self.assertRaises(ValidationError) as context:
            sale.full_clean()
        self.assertIn('pay_method', context.exception.message_dict)


class SaleDetailModelTestCase(TenantTestCase, TestCase):
    """Test SaleDetail model validations and properties"""
    
    def setUp(self):
        super().setUp()
        # Already have self.user from TenantTestCase # User.objects.create_user(username='detailtest', password='test')
        self.branch = create_test_branch(company=self.company, code="TB2")
        
        cash_register = CashRegister.objects.create(company=self.company, 
            branch=self.branch,
            code='TEST-DETAIL-01',
            name='Detail Test Register',
            is_active=True
        )
        self.cash_session = CashSession.objects.create(company=self.company, 
            cash_register=cash_register,
            user=self.user,
            opening_balance=Decimal('1000.00'),
            status=SessionStatus.OPEN
        )
        
        self.sale = Sale.objects.create(company=self.company, seller=self.user, cash_session=self.cash_session)
        
        # Create product
        category = Category.objects.create(company=self.company, name='DetailCat')
        brand = Brand.objects.create(company=self.company, name='DetailBrand')
        season = Season.objects.create(name='DetailSeason')
        color = Color.objects.create(name='DetailColor', code='#123456')
        gender = Gender.objects.create(name='Female')
        
        self.product = Product.objects.create(
            company=self.company,
            name='DetailProduct',
            category=category,
            brand=brand,
            season=season,
            color=color,
            gender=gender,
            sale_price=Decimal('150.00'),
            cost_price=Decimal('75.00')
        )
        
        # Update inventory
        inventory = Inventory.objects.get(product=self.product)
        inventory.quantity = 50
        inventory.save()
    
    def test_sale_detail_str(self):
        """Test SaleDetail __str__ method"""
        detail = SaleDetail.objects.create(company=self.company, 
            order=self.sale,
            product=self.product,
            quantity=3,
            sale_price=150,
            cost_price=75
        )
        str_repr = str(detail)
        self.assertIn('DetailProduct', str_repr)
        self.assertIn('3', str_repr)
    
    def test_sale_detail_clean_requires_product(self):
        """Test that SaleDetail requires product"""
        detail = SaleDetail(order=self.sale, quantity=1, sale_price=100, cost_price=50)
        detail.product = None
        
        with self.assertRaises(ValidationError) as context:
            detail.full_clean()
        self.assertIn('product', context.exception.message_dict)
    
    def test_sale_detail_clean_requires_positive_quantity(self):
        """Test that quantity must be greater than zero"""
        detail = SaleDetail(
            order=self.sale,
            product=self.product,
            quantity=0,  # Invalid
            sale_price=100,
            cost_price=50
        )
        
        with self.assertRaises(ValidationError) as context:
            detail.full_clean()
        self.assertIn('quantity', context.exception.message_dict)
    
    def test_sale_detail_clean_insufficient_stock(self):
        """Test stock validation"""
        # Set inventory to 5
        inventory = Inventory.objects.get(product=self.product)
        inventory.quantity = 5
        inventory.save()
        
        # Try to create detail with quantity 10 (more than available)
        detail = SaleDetail(
            order=self.sale,
            product=self.product,
            quantity=10,
            sale_price=150,
            cost_price=75
        )
        
        with self.assertRaises(ValidationError) as context:
            detail.full_clean()
        self.assertIn('quantity', context.exception.message_dict)


class ModelEdgeCaseTests(TenantTestCase, TestCase):
    """Tests for model edge cases"""
    
    def setUp(self):
        super().setUp()
        # Already have self.user from TenantTestCase
        self.branch = create_test_branch(company=self.company, code="TB3")
        cr = CashRegister.objects.create(company=self.company, branch=self.branch, code='M2', name='M2', is_active=True)
        self.session = CashSession.objects.create(company=self.company, 
            cash_register=cr, user=self.user,
            opening_balance=Decimal('1000'), status=SessionStatus.OPEN
        )
        
    def test_saledetail_does_not_exist_exception(self):
        """SaleDetail.DoesNotExist exception in clean() handling"""
        cat = Category.objects.create(company=self.company, name='ExCat')
        br = Brand.objects.create(company=self.company, name='ExBr')
        se = Season.objects.create(name='ExSe')
        co = Color.objects.create(name='ExCo', code='#333')
        ge = Gender.objects.create(name='ExGe')
        
        prod = Product.objects.create(
            company=self.company,
            name='ExProd', category=cat, brand=br, season=se,
            color=co, gender=ge, sale_price=Decimal('100'), cost_price=Decimal('50')
        )
        
        # Set inventory
        inv = Inventory.objects.get(product=prod)
        inv.quantity = 100
        inv.save()
        
        sale = Sale.objects.create(company=self.company, seller=self.user, cash_session=self.session)
        
        # Create detail with non-existent pk to trigger DoesNotExist
        detail = SaleDetail(
            pk=999999,  # Non-existent
            order=sale,
            product=prod,
            quantity=1,
            sale_price=100,
            cost_price=50
        )
        
        # Should handle DoesNotExist gracefully
        try:
            detail.full_clean()
        except ValidationError:
            pass
        
    def test_profit_margin_zero(self):
        """profit_margin with zero total"""
        cat = Category.objects.create(company=self.company, name='PC')
        br = Brand.objects.create(company=self.company, name='PB')
        se = Season.objects.create(name='PS')
        co = Color.objects.create(name='PCo', code='#222')
        ge = Gender.objects.create(name='PG')
        
        prod = Product.objects.create(
            company=self.company,
            name='PP', category=cat, brand=br, season=se,
            color=co, gender=ge, sale_price=Decimal('0'), cost_price=Decimal('50')
        )
        
        sale = Sale.objects.create(company=self.company, seller=self.user, cash_session=self.session)
        
        # Create detail with zero sale price
        detail = SaleDetail(order=sale, product=prod, quantity=1, sale_price=0, cost_price=50)
        # profit_margin should be 0 when total_price is 0
        self.assertEqual(detail.profit_margin, Decimal('0.00'))

    def test_save_zero_sale_price_preserved(self):
        """BUG-1: Decimal('0.00') sale_price should NOT be overwritten by product price"""
        cat = Category.objects.create(company=self.company, name='ZC')
        br = Brand.objects.create(company=self.company, name='ZB')
        se = Season.objects.create(name='ZS')
        co = Color.objects.create(name='ZCo', code='#333')
        ge = Gender.objects.create(name='ZG')
        prod = Product.objects.create(
            company=self.company,
            name='ZP', category=cat, brand=br, season=se,
            color=co, gender=ge, sale_price=Decimal('100'), cost_price=Decimal('50')
        )
        inv = Inventory.objects.get(product=prod)
        inv.quantity = 50
        inv.save()
        sale = Sale.objects.create(company=self.company, seller=self.user, cash_session=self.session)
        detail = SaleDetail(
            order=sale, product=prod,
            quantity=1, sale_price=Decimal('0.00'), cost_price=Decimal('0.00')
        )
        detail.save()
        detail.refresh_from_db()
        self.assertEqual(detail.sale_price, Decimal('0.00'))
        self.assertEqual(detail.cost_price, Decimal('0.00'))

    def test_save_none_price_gets_product_price(self):
        """BUG-1: None sale_price should be auto-filled from product"""
        cat = Category.objects.create(company=self.company, name='NC')
        br = Brand.objects.create(company=self.company, name='NB')
        se = Season.objects.create(name='NS')
        co = Color.objects.create(name='NCo', code='#444')
        ge = Gender.objects.create(name='NG')
        prod = Product.objects.create(
            company=self.company,
            name='NP', category=cat, brand=br, season=se,
            color=co, gender=ge, sale_price=Decimal('150'), cost_price=Decimal('75')
        )
        inv = Inventory.objects.get(product=prod)
        inv.quantity = 50
        inv.save()
        sale = Sale.objects.create(company=self.company, seller=self.user, cash_session=self.session)
        detail = SaleDetail(
            order=sale, product=prod,
            quantity=1, sale_price=None, cost_price=None
        )
        detail.save()
        detail.refresh_from_db()
        self.assertEqual(detail.sale_price, Decimal('150.00'))
        self.assertEqual(detail.cost_price, Decimal('75.00'))

    def test_clean_prevents_adding_to_closed_sale(self):
        """MISSING-1: Cannot add items to a closed sale"""
        cat = Category.objects.create(company=self.company, name='CC')
        br = Brand.objects.create(company=self.company, name='CB')
        se = Season.objects.create(name='CS')
        co = Color.objects.create(name='CCo', code='#555')
        ge = Gender.objects.create(name='CG')
        prod = Product.objects.create(
            company=self.company,
            name='CP', category=cat, brand=br, season=se,
            color=co, gender=ge, sale_price=Decimal('10'), cost_price=Decimal('5')
        )
        closed_sale = Sale.objects.create(company=self.company, 
            seller=self.user, cash_session=self.session, closed=True
        )
        detail = SaleDetail(
            order=closed_sale, product=prod,
            quantity=1, sale_price=Decimal('10.00'), cost_price=Decimal('5.00')
        )
        with self.assertRaises(ValidationError) as ctx:
            detail.full_clean()
        self.assertIn('order', ctx.exception.message_dict)

    def test_clean_prevents_adding_to_canceled_sale(self):
        """MISSING-1: Cannot add items to a canceled sale"""
        cat = Category.objects.create(company=self.company, name='XC')
        br = Brand.objects.create(company=self.company, name='XB')
        se = Season.objects.create(name='XS')
        co = Color.objects.create(name='XCo', code='#666')
        ge = Gender.objects.create(name='XG')
        prod = Product.objects.create(
            company=self.company,
            name='XP', category=cat, brand=br, season=se,
            color=co, gender=ge, sale_price=Decimal('10'), cost_price=Decimal('5')
        )
        canceled_sale = Sale.objects.create(company=self.company, 
            seller=self.user, cash_session=self.session, canceled=True
        )
        detail = SaleDetail(
            order=canceled_sale, product=prod,
            quantity=1, sale_price=Decimal('10.00'), cost_price=Decimal('5.00')
        )
        with self.assertRaises(ValidationError) as ctx:
            detail.full_clean()
        self.assertIn('order', ctx.exception.message_dict)


# ============================================================
# Tests consolidated from test_signals.py, test_signal_*.py
# ============================================================
class SignalsTests(TenantTestCase, TestCase):
    """Signal tests - consolidated from test_signals.py and test_signal_*.py"""
    
    def setUp(self):
        super().setUp()
        
        # Setup Cash Session
        self.branch = create_test_branch(company=self.company, code="TB4")
        cr = CashRegister.objects.create(company=self.company, branch=self.branch, code='S1', name='S1', is_active=True)
        self.session = CashSession.objects.create(company=self.company, 
            cash_register=cr,
            user=self.user,
            opening_balance=Decimal('1000'),
            status=SessionStatus.OPEN
        )
        
        # Setup Product
        cat = Category.objects.create(company=self.company, name='SigCat')
        br = Brand.objects.create(company=self.company, name='SigBr')
        se = Season.objects.create(name='SigSe')
        co = Color.objects.create(name='SigCo', code='#FFF')
        ge = Gender.objects.create(name='SigGe')
        
        self.prod = Product.objects.create(
            company=self.company,
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
            Inventory.objects.filter(product=self.prod).delete()
        except:
            pass
            
        # Refresh prod to clear likely cached relation
        self.prod.refresh_from_db()
        
        sale = Sale.objects.create(company=self.company, seller=self.user, cash_session=self.session)
        
        # Create detail - should trigger signal and raise ValidationError because no inventory
        with self.assertRaises(ValidationError):
            SaleDetail.objects.create(company=self.company, 
                order=sale,
                product=self.prod,
                quantity=1,
                sale_price=Decimal('10'),
                cost_price=Decimal('5')
            )

    def test_saledetail_clean_no_inventory(self):
        """Test clean() raises ValidationError when product has no inventory in branch"""
        # Create product without inventory
        try:
            Inventory.objects.filter(product=self.prod).delete()
        except:
            pass
            
        sale = Sale.objects.create(company=self.company, seller=self.user, cash_session=self.session)
        detail = SaleDetail(company=self.company, 
            order=sale,
            product=self.prod,
            quantity=1,
            sale_price=Decimal('10'),
            cost_price=Decimal('5')
        )
        
        with self.assertRaises(ValidationError) as ctx:
            detail.full_clean()
        
        self.assertIn('product', ctx.exception.message_dict)

    def test_update_stock_negative_prevention(self):
        """Test signal preventing negative stock"""
        # Set stock to 5
        self.inventory.quantity = 5
        self.inventory.save()
        
        sale = Sale.objects.create(company=self.company, seller=self.user, cash_session=self.session)
        
        # Try to sell 10. clean() prevents this usually, but we want to hit the signal check.
        detail = SaleDetail(
            order=sale,
            product=self.prod,
            quantity=10,
            sale_price=Decimal('10'),
            cost_price=Decimal('5')
        )
        
        # Signal runs on save
        with self.assertRaises(ValidationError):
            detail.save()

    def test_restore_stock_on_delete(self):
        """Test stock restoration on SaleDetail delete"""
        
        sale = Sale.objects.create(company=self.company, seller=self.user, cash_session=self.session)
        detail = SaleDetail.objects.create(company=self.company, 
            order=sale,
            product=self.prod,
            quantity=5,
            sale_price=Decimal('10'),
            cost_price=Decimal('5')
        )
        
        # Test basic delete signal works normally
        detail.delete()
        self.prod.refresh_from_db()
        # Quantity should be restored (100 is default, we consumed 5 via signal on create, then restored)
        inv = Inventory.objects.get(product=self.prod)
        self.assertEqual(inv.quantity, 100)

    def test_restore_stock_delete_no_inventory(self):
        """Test delete signal when inventory does not exist"""
        sale = Sale.objects.create(company=self.company, seller=self.user, cash_session=self.session)
        detail = SaleDetail.objects.create(company=self.company, 
            order=sale,
            product=self.prod,
            quantity=5,
            sale_price=Decimal('10'),
            cost_price=Decimal('5')
        )
        # Delete inventory after creation
        Inventory.objects.filter(product=self.prod).delete()
        # Delete detail should not raise error (covers lines 60-61)
        try:
            detail.delete()
        except Exception as e:
            self.fail(f"delete() raised an exception: {e}")

    def test_accounting_no_customer_account(self):
        """Test integration when client has no customer account"""
        client = Client.objects.create(company=self.company, 
            name='NoAccount', 
            last_name='Client', 
            dni='111', 
            approved_customer_account=False
        )
        # Ensure no account exists (delete if auto-created)
        if hasattr(client, 'customer_account'):
            client.customer_account.delete()
            client.refresh_from_db()
            
        sale = Sale.objects.create(company=self.company, 
            seller=self.user,
            cash_session=self.session,
            client=client,
            closed=False
        )
        
        # Close sale
        sale.closed = True
        sale.save()

    def test_accounting_inactive_account(self):
        """Test integration when customer account is inactive"""
        from clients.models import CustomerBalanceRecord
        
        client = Client.objects.create(company=self.company, name='Inactive', last_name='Client', dni='222')
        account = client.customer_account
        account.active = False
        account.save()
        
        sale = Sale.objects.create(company=self.company, 
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
        from clients.models import CustomerBalanceRecord
        from clients.choices import MovementType
        
        client = Client.objects.create(company=self.company, name='Dupe', last_name='Client', dni='333')
        account = client.customer_account
        
        sale = Sale.objects.create(company=self.company, 
            seller=self.user,
            cash_session=self.session,
            client=client,
            closed=False
        )
        
        # Manually create a balance record to simulate "already processed"
        existing_record = CustomerBalanceRecord.objects.create(company=self.company, customer_account=account,
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

    def test_sale_detail_creation_triggers_inventory_update(self):
        """Test that creating a sale detail updates inventory"""
        inv = Inventory.objects.get(product=self.prod)
        initial_qty = inv.quantity
        
        # Create sale detail
        sale = Sale.objects.create(company=self.company, seller=self.user, cash_session=self.session)
        detail = SaleDetail.objects.create(
            company=self.company,
            order=sale,
            product=self.prod,
            quantity=2,
            sale_price=Decimal('100.00'),
            cost_price=Decimal('50.00')
        )
        
        # Check inventory was updated
        inv.refresh_from_db()
        self.assertEqual(inv.quantity, initial_qty - 2)

    def test_sale_detail_without_product(self):
        """Test sale detail without product doesn't crash"""
        sale = Sale.objects.create(company=self.company, seller=self.user, cash_session=self.session)
        detail = SaleDetail.objects.create(
            company=self.company,
            order=sale,
            product=None,
            quantity=1,
            sale_price=Decimal('100.00'),
            cost_price=Decimal('50.00')
        )
        
        self.assertIsNone(detail.product)
    
    def test_cache_old_quantity_doesnotexist(self):
        """Test cache_old_quantity when SaleDetail doesn't exist (edge case coverage)"""
        sale = Sale.objects.create(company=self.company, seller=self.user, cash_session=self.session)
        
        # Create a detail with a specific pk that doesn't exist in DB yet
        detail = SaleDetail(
            company=self.company,
            order=sale,
            product=self.prod,
            quantity=5,
            sale_price=Decimal('100.00'),
            cost_price=Decimal('50.00')
        )
        # Manually set pk to trigger the if instance.pk branch
        detail.pk = 999999999  # Non-existent ID
        
        # This should trigger the except SaleDetail.DoesNotExist block
        # We can't directly call the signal, but we can test via save which triggers it
        try:
            detail.save()
        except:
            pass  # Expected to fail due to other validations, but signal code was executed
        
        # Verify _old_quantity was set to 0 when DoesNotExist was caught
        self.assertTrue(hasattr(detail, '_old_quantity'))
        self.assertEqual(detail._old_quantity, 0)


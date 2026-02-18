from decimal import Decimal
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from sales.models import Sale, SaleDetail, PayMethod
from clients.models import Client
from products.models import Product, Category, Brand, Season, Color, Gender
from devices.models import CashRegister
from cash.models import CashSession
from cash.choices import SessionStatus
from inventory.models import Inventory

User = get_user_model()


class PayMethodModelTestCase(TestCase):
    """Test PayMethod model"""
    
    def test_paymethod_str(self):
        """Test PayMethod __str__ method"""
        pay_method = PayMethod.objects.create(name='Tarjeta de Crédito')
        self.assertEqual(str(pay_method), 'Tarjeta de Crédito')


class SaleModelTestCase(TestCase):
    """Test Sale model __str__ and validations"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testmodel',
            password='test',
            first_name='John',
            last_name='Doe'
        )
        self.client_obj = Client.objects.create(name='TestClient', last_name='Model', dni='456')
        
        cash_register = CashRegister.objects.create(
            code='TEST-MODEL-01',
            name='Model Test Register',
            is_active=True
        )
        self.cash_session = CashSession.objects.create(
            cash_register=cash_register,
            user=self.user,
            opening_balance=Decimal('1000.00'),
            status=SessionStatus.OPEN
        )
        
        self.pay_method = PayMethod.objects.create(name='Efectivo')
    
    def test_sale_str_with_client(self):
        """Test Sale __str__ with client"""
        sale = Sale.objects.create(
            seller=self.user,
            client=self.client_obj,
            cash_session=self.cash_session
        )
        str_repr = str(sale)
        self.assertIn('TestClient', str_repr)
        self.assertIn('John Doe', str_repr)
    
    def test_sale_clean_closed_requires_cash_session(self):
        """Test that closed sales require cash_session"""
        sale = Sale.objects.create(seller=self.user)
        sale.closed = True
        sale.cash_session = None  # No cash session
        
        with self.assertRaises(ValidationError) as context:
            sale.full_clean()
        self.assertIn('cash_session', context.exception.message_dict)
    
    def test_sale_clean_closed_requires_pay_method(self):
        """Test that closed sales require pay_method"""
        sale = Sale.objects.create(seller=self.user, cash_session=self.cash_session)
        sale.closed = True
        sale.pay_method = None
        
        with self.assertRaises(ValidationError) as context:
            sale.full_clean()
        self.assertIn('pay_method', context.exception.message_dict)


class SaleDetailModelTestCase(TestCase):
    """Test SaleDetail model validations and properties"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='detailtest', password='test')
        
        cash_register = CashRegister.objects.create(
            code='TEST-DETAIL-01',
            name='Detail Test Register',
            is_active=True
        )
        self.cash_session = CashSession.objects.create(
            cash_register=cash_register,
            user=self.user,
            opening_balance=Decimal('1000.00'),
            status=SessionStatus.OPEN
        )
        
        self.sale = Sale.objects.create(seller=self.user, cash_session=self.cash_session)
        
        # Create product
        category = Category.objects.create(name='DetailCat')
        brand = Brand.objects.create(name='DetailBrand')
        season = Season.objects.create(name='DetailSeason')
        color = Color.objects.create(name='DetailColor', code='#123456')
        gender = Gender.objects.create(name='Female')
        
        self.product = Product.objects.create(
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
        detail = SaleDetail.objects.create(
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


class ModelEdgeCaseTests(TestCase):
    """Tests for model edge cases"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='mod', password='test')
        cr = CashRegister.objects.create(code='M2', name='M2', is_active=True)
        self.session = CashSession.objects.create(
            cash_register=cr, user=self.user,
            opening_balance=Decimal('1000'), status=SessionStatus.OPEN
        )
        
    def test_saledetail_does_not_exist_exception(self):
        """SaleDetail.DoesNotExist exception in clean() handling"""
        cat = Category.objects.create(name='ExCat')
        br = Brand.objects.create(name='ExBr')
        se = Season.objects.create(name='ExSe')
        co = Color.objects.create(name='ExCo', code='#333')
        ge = Gender.objects.create(name='ExGe')
        
        prod = Product.objects.create(
            name='ExProd', category=cat, brand=br, season=se,
            color=co, gender=ge, sale_price=Decimal('100'), cost_price=Decimal('50')
        )
        
        # Set inventory
        inv = Inventory.objects.get(product=prod)
        inv.quantity = 100
        inv.save()
        
        sale = Sale.objects.create(seller=self.user, cash_session=self.session)
        
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
        cat = Category.objects.create(name='PC')
        br = Brand.objects.create(name='PB')
        se = Season.objects.create(name='PS')
        co = Color.objects.create(name='PCo', code='#222')
        ge = Gender.objects.create(name='PG')
        
        prod = Product.objects.create(
            name='PP', category=cat, brand=br, season=se,
            color=co, gender=ge, sale_price=Decimal('0'), cost_price=Decimal('50')
        )
        
        sale = Sale.objects.create(seller=self.user, cash_session=self.session)
        
        # Create detail with zero sale price
        detail = SaleDetail(order=sale, product=prod, quantity=1, sale_price=0, cost_price=50)
        # profit_margin should be 0 when total_price is 0
        self.assertEqual(detail.profit_margin, Decimal('0.00'))

    def test_save_zero_sale_price_preserved(self):
        """BUG-1: Decimal('0.00') sale_price should NOT be overwritten by product price"""
        cat = Category.objects.create(name='ZC')
        br = Brand.objects.create(name='ZB')
        se = Season.objects.create(name='ZS')
        co = Color.objects.create(name='ZCo', code='#333')
        ge = Gender.objects.create(name='ZG')
        prod = Product.objects.create(
            name='ZP', category=cat, brand=br, season=se,
            color=co, gender=ge, sale_price=Decimal('100'), cost_price=Decimal('50')
        )
        inv = Inventory.objects.get(product=prod)
        inv.quantity = 50
        inv.save()
        sale = Sale.objects.create(seller=self.user, cash_session=self.session)
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
        cat = Category.objects.create(name='NC')
        br = Brand.objects.create(name='NB')
        se = Season.objects.create(name='NS')
        co = Color.objects.create(name='NCo', code='#444')
        ge = Gender.objects.create(name='NG')
        prod = Product.objects.create(
            name='NP', category=cat, brand=br, season=se,
            color=co, gender=ge, sale_price=Decimal('150'), cost_price=Decimal('75')
        )
        inv = Inventory.objects.get(product=prod)
        inv.quantity = 50
        inv.save()
        sale = Sale.objects.create(seller=self.user, cash_session=self.session)
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
        cat = Category.objects.create(name='CC')
        br = Brand.objects.create(name='CB')
        se = Season.objects.create(name='CS')
        co = Color.objects.create(name='CCo', code='#555')
        ge = Gender.objects.create(name='CG')
        prod = Product.objects.create(
            name='CP', category=cat, brand=br, season=se,
            color=co, gender=ge, sale_price=Decimal('10'), cost_price=Decimal('5')
        )
        closed_sale = Sale.objects.create(
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
        cat = Category.objects.create(name='XC')
        br = Brand.objects.create(name='XB')
        se = Season.objects.create(name='XS')
        co = Color.objects.create(name='XCo', code='#666')
        ge = Gender.objects.create(name='XG')
        prod = Product.objects.create(
            name='XP', category=cat, brand=br, season=se,
            color=co, gender=ge, sale_price=Decimal('10'), cost_price=Decimal('5')
        )
        canceled_sale = Sale.objects.create(
            seller=self.user, cash_session=self.session, canceled=True
        )
        detail = SaleDetail(
            order=canceled_sale, product=prod,
            quantity=1, sale_price=Decimal('10.00'), cost_price=Decimal('5.00')
        )
        with self.assertRaises(ValidationError) as ctx:
            detail.full_clean()
        self.assertIn('order', ctx.exception.message_dict)


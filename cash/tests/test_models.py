from decimal import Decimal
from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError

from devices.models import CashRegister
from cash.models import CashSession, CashMovement
from cash.choices import SessionStatus, MovementType
from sales.models import Sale, SaleDetail, PayMethod
from products.models import Product, Category, Brand, Season, Color, Gender
from inventory.models import Inventory

User = get_user_model()


class ModelPropertiesTestCase(TestCase):
    """Tests for model properties"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='proptest',
            password='test',
            first_name='Prop',
            last_name='Test'
        )
        self.cash_register = CashRegister.objects.create(
            code='PROP-01',
            name='Property Test Register',
            is_active=True
        )
        
    def test_total_cash_sales_property(self):
        """Test total_cash_sales property"""
        session = CashSession.objects.create(
            cash_register=self.cash_register,
            user=self.user,
            opening_balance=Decimal('1000.00'),
            status=SessionStatus.OPEN
        )
        
        # Create products for sales
        category = Category.objects.create(name='TestCat')
        brand = Brand.objects.create(name='TestBrand')
        season = Season.objects.create(name='TestSeason')
        color = Color.objects.create(name='TestColor', code='#123456')
        gender = Gender.objects.create(name='TestGender')
        
        product = Product.objects.create(
            name='TestProduct',
            category=category,
            brand=brand,
            season=season,
            color=color,
            gender=gender,
            sale_price=Decimal('100.00'),
            cost_price=Decimal('50.00')
        )
        
        # Update inventory
        inventory = Inventory.objects.get(product=product)
        inventory.quantity = 100
        inventory.save()
        
        # Create pay method
        pay_method = PayMethod.objects.create(name='Cash')
        
        # Create sale
        sale = Sale.objects.create(
            seller=self.user,
            cash_session=session,
            pay_method=pay_method,
            closed=True,
            total_amount=Decimal('200.00')
        )
        
        # Create detail
        SaleDetail.objects.create(
            order=sale,
            product=product,
            quantity=2,
            sale_price=100,
            cost_price=50
        )
        
        # Test property
        total = session.total_cash_sales
        self.assertGreater(total, Decimal('0.00'))
        
    def test_total_cash_in_property(self):
        """Test total_cash_in property"""
        session = CashSession.objects.create(
            cash_register=self.cash_register,
            user=self.user,
            opening_balance=Decimal('1000.00'),
            status=SessionStatus.OPEN
        )
        
        # Create cash in movement
        CashMovement.objects.create(
            cash_session=session,
            type=MovementType.CASH_IN,
            amount=Decimal('500.00'),
            reason='Test cash in',
            created_by=self.user
        )
        
        # Test property
        total_in = session.total_cash_in
        self.assertEqual(total_in, Decimal('500.00'))
        
    def test_total_cash_out_property(self):
        """Test total_cash_out property"""
        session = CashSession.objects.create(
            cash_register=self.cash_register,
            user=self.user,
            opening_balance=Decimal('1000.00'),
            status=SessionStatus.OPEN
        )
        
        # Create cash out movement
        CashMovement.objects.create(
            cash_session=session,
            type=MovementType.CASH_OUT,
            amount=Decimal('200.00'),
            reason='Test cash out',
            created_by=self.user
        )
        
        # Test property
        total_out = session.total_cash_out
        self.assertEqual(total_out, Decimal('200.00'))
        
    def test_expected_balance_property(self):
        """Test expected_balance property"""
        session = CashSession.objects.create(
            cash_register=self.cash_register,
            user=self.user,
            opening_balance=Decimal('1000.00'),
            status=SessionStatus.OPEN
        )
        
        # Create movements
        CashMovement.objects.create(
            cash_session=session,
            type=MovementType.CASH_IN,
            amount=Decimal('300.00'),
            reason='Cash in',
            created_by=self.user
        )
        CashMovement.objects.create(
            cash_session=session,
            type=MovementType.CASH_OUT,
            amount=Decimal('100.00'),
            reason='Cash out',
            created_by=self.user
        )
        
        # Expected: 1000 + 0 (no sales) + 300 - 100 = 1200
        expected = session.expected_balance
        self.assertEqual(expected, Decimal('1200.00'))
        
    def test_difference_property_with_closing(self):
        """Test difference property when closing_balance exists"""
        session = CashSession.objects.create(
            cash_register=self.cash_register,
            user=self.user,
            opening_balance=Decimal('1000.00'),
            closing_balance=Decimal('1250.00'),
            status=SessionStatus.CLOSED,
            closing_date=timezone.now()
        )
        
        # Difference = 1250 - 1000 = 250
        diff = session.difference
        self.assertEqual(diff, Decimal('250.00'))
        
    def test_sales_count_property(self):
        """Test sales_count property"""
        session = CashSession.objects.create(
            cash_register=self.cash_register,
            user=self.user,
            opening_balance=Decimal('1000.00'),
            status=SessionStatus.OPEN
        )
        
        # Create products
        category = Category.objects.create(name='CountCat')
        brand = Brand.objects.create(name='CountBrand')
        season = Season.objects.create(name='CountSeason')
        color = Color.objects.create(name='CountColor', code='#AABBCC')
        gender = Gender.objects.create(name='CountGender')
        
        product = Product.objects.create(
            name='CountProduct',
            category=category,
            brand=brand,
            season=season,
            color=color,
            gender=gender,
            sale_price=Decimal('100.00'),
            cost_price=Decimal('50.00')
        )
        
        inventory = Inventory.objects.get(product=product)
        inventory.quantity = 100
        inventory.save()
        
        pay_method = PayMethod.objects.create(name='CountCash')
        
        # Create closed sales
        for i in range(3):
            sale = Sale.objects.create(
                seller=self.user,
                cash_session=session,
                pay_method=pay_method,
                closed=True
            )
            SaleDetail.objects.create(
                order=sale,
                product=product,
                quantity=1,
                sale_price=100,
                cost_price=50
            )
        
        # Create canceled sale (should not count)
        canceled_sale = Sale.objects.create(
            seller=self.user,
            cash_session=session,
            pay_method=pay_method,
            closed=True,
            canceled=True
        )
        
        # Test property
        count = session.sales_count
        self.assertEqual(count, 3)  # Only non-canceled sales

    def test_cash_session_str_method(self):
        """Test CashSession __str__ method"""
        session = CashSession.objects.create(
            cash_register=self.cash_register,
            user=self.user,
            opening_balance=Decimal('1000.00'),
            status=SessionStatus.OPEN
        )
        
        # Test __str__ method
        str_repr = str(session)
        self.assertIn(self.cash_register.name, str_repr)
        self.assertIn(self.user.get_full_name(), str_repr)
    
    def test_cash_movement_str_method(self):
        """Test CashMovement __str__ method"""
        session = CashSession.objects.create(
            cash_register=self.cash_register,
            user=self.user,
            opening_balance=Decimal('1000.00'),
            status=SessionStatus.OPEN
        )
        
        movement = CashMovement.objects.create(
            cash_session=session,
            type=MovementType.CASH_IN,
            amount=Decimal('500.00'),
            reason='Test reason',
            created_by=self.user
        )
        
        # Test __str__ method
        str_repr = str(movement)
        self.assertIn('500', str_repr)
        self.assertIn('Test reason', str_repr)

    def test_cash_session_validation_opening_balance_negative(self):
        """Test validation: negative opening balance"""
        session = CashSession(
            cash_register=self.cash_register,
            user=self.user,
            opening_balance=Decimal('-100.00'),
            status=SessionStatus.OPEN
        )
        
        with self.assertRaises(ValidationError) as context:
            session.full_clean()
        
        self.assertIn('opening_balance', context.exception.message_dict)
    
    def test_cash_session_validation_closing_balance_required(self):
        """Test validation: closing balance required when closed"""
        session = CashSession.objects.create(
            cash_register=self.cash_register,
            user=self.user,
            opening_balance=Decimal('1000.00'),
            status=SessionStatus.OPEN
        )
        
        # Try to close without closing_balance
        session.status = SessionStatus.CLOSED
        session.closing_date = timezone.now()
        
        with self.assertRaises(ValidationError) as context:
            session.full_clean()
        
        errors = context.exception.message_dict
        self.assertIn('closing_balance', errors)

    def test_cash_session_validation_closing_date_required(self):
        """Test validation: closing date required when closed"""
        session = CashSession.objects.create(
            cash_register=self.cash_register,
            user=self.user,
            opening_balance=Decimal('1000.00'),
            status=SessionStatus.OPEN
        )
        
        # Try to close without closing_date
        session.status = SessionStatus.CLOSED
        session.closing_balance = Decimal('1500.00')
        session.closing_date = None
        
        with self.assertRaises(ValidationError) as context:
            session.full_clean()
        
        self.assertIn('closing_date', context.exception.message_dict)
    
    def test_cash_movement_validation_zero_amount(self):
        """Test validation: amount must be greater than zero"""
        session = CashSession.objects.create(
            cash_register=self.cash_register,
            user=self.user,
            opening_balance=Decimal('1000.00'),
            status=SessionStatus.OPEN
        )
        
        movement = CashMovement(
            cash_session=session,
            type=MovementType.CASH_IN,
            amount=Decimal('0.00'),
            reason='Test',
            created_by=self.user
        )
        
        with self.assertRaises(ValidationError) as context:
            movement.full_clean()
        
        self.assertIn('amount', context.exception.message_dict)
    
    def test_cash_movement_validation_closed_session(self):
        """Test validation: cannot add movements to closed session"""
        session = CashSession.objects.create(
            cash_register=self.cash_register,
            user=self.user,
            opening_balance=Decimal('1000.00'),
            status=SessionStatus.CLOSED,
            closing_balance=Decimal('1500.00'),
            closing_date=timezone.now()
        )
        
        movement = CashMovement(
            cash_session=session,
            type=MovementType.CASH_IN,
            amount=Decimal('100.00'),
            reason='Test',
            created_by=self.user
        )
        
        with self.assertRaises(ValidationError) as context:
            movement.full_clean()
        
        self.assertIn('cash_session', context.exception.message_dict)

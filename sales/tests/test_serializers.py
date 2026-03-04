from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from utils.tests import TenantTestCase, create_test_branch

from sales.models import Sale, SaleDetail, PayMethod
from sales.serializers import SaleSerializer, SaleDetailSerializer
from clients.models import Client
from products.models import Product, Category, Brand, Season, Color, Gender
from devices.models import CashRegister
from cash.models import CashSession
from cash.choices import SessionStatus
from inventory.models import Inventory


User = get_user_model()


class SaleSerializerTestCase(TenantTestCase, TestCase):
    def setUp(self):
        super().setUp()
        user = self.user # User.objects.create_user(username='testser', password='test')
        self.branch = create_test_branch(company=self.company, code="TBs1")
        
        cash_register = CashRegister.objects.create(company=self.company, 
            branch=self.branch,
            code='TEST-SER-01',
            name='Serializer Test Register',
            is_active=True
        )
        cash_session = CashSession.objects.create(company=self.company, 
            cash_register=cash_register,
            user=user,
            opening_balance=Decimal('1000.00'),
            status=SessionStatus.OPEN
        )
        
        self.client_obj = Client.objects.create(company=self.company, name="Juan", last_name="Perez", dni="123")
        self.pay_method = PayMethod.objects.create(company=self.company, name="Efectivo")
        self.sale = Sale.objects.create(company=self.company, 
            client=self.client_obj,
            pay_method=self.pay_method,
            seller=user,
            cash_session=cash_session
        )


    def test_sale_serializer(self):
        serializer = SaleSerializer(self.sale)
        data = serializer.data
        self.assertIn('client_data', data)
        self.assertEqual(data['client_data']['name'], "Juan")

class SaleDetailSerializerTestCase(TenantTestCase, TestCase):
    def setUp(self):
        super().setUp()
        user = self.user # User.objects.create_user(username='testserdet', password='test')
        self.branch = create_test_branch(company=self.company, code="TBs2")
        
        cash_register = CashRegister.objects.create(company=self.company, 
            branch=self.branch,
            code='TEST-SER-02',
            name='Serializer Test Register 2',
            is_active=True
        )
        cash_session = CashSession.objects.create(company=self.company, 
            cash_register=cash_register,
            user=user,
            opening_balance=Decimal('1000.00'),
            status=SessionStatus.OPEN
        )
        
        self.client_obj = Client.objects.create(company=self.company, name="Juan", last_name="Perez", dni="123")
        self.sale = Sale.objects.create(company=self.company, 
            client=self.client_obj,
            seller=user,
            cash_session=cash_session
        )
        
        self.category = Category.objects.create(company=self.company, name="Cat")
        self.brand = Brand.objects.create(company=self.company, name="Brand")
        self.season = Season.objects.create(name="Season")
        self.color = Color.objects.create(name="Color", code="#000000")
        self.gender = Gender.objects.create(name="Unisex")
        self.product = Product.objects.create(
            company=self.company,
            name="Prod", category=self.category, brand=self.brand, season=self.season,
            color=self.color, gender=self.gender, sale_price=100, cost_price=50
        )
        # Inventory auto-created by product signal, update quantity for testing
        inventory = Inventory.objects.get(product=self.product)
        inventory.quantity = 100
        inventory.save()
        
        self.detail = SaleDetail.objects.create(company=self.company, 

            order=self.sale, product=self.product, quantity=2, 
            sale_price=100, cost_price=50
        )



    def test_sale_detail_serializer(self):
        serializer = SaleDetailSerializer(self.detail)
        data = serializer.data
        self.assertIn('product_data', data)

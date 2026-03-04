from django.test import TestCase
from inventory.models import Inventory
from inventory.serializers import InventorySerializer
from products.models import Product, Category, Brand, Season, Color, Gender
from utils.tests import TenantTestCase, create_test_branch

class InventorySerializerTestCase(TenantTestCase, TestCase):
    def setUp(self):
        super().setUp()
        self.branch = create_test_branch(company=self.company)
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
        self.inventory = Inventory.objects.get(product=self.product)

    def test_inventory_serializer(self):
        serializer = InventorySerializer(self.inventory)
        data = serializer.data
        self.assertEqual(data['quantity'], 0)

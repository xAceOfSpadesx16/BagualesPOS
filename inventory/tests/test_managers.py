from django.test import TestCase
from inventory.models import Inventory
from products.models import Product, Category, Brand, Season, Color, Gender
from utils.tests import TenantTestCase, create_test_branch

class InventoryManagerTestCase(TenantTestCase, TestCase):
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

    def test_sr_product_relateds(self):
        qs = Inventory.objects.sr_product_relateds()
        self.assertIn(self.inventory, qs)
        self.assertEqual(qs.count(), 1)

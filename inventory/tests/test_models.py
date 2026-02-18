from django.test import TestCase
from inventory.models import Inventory
from products.models import Product, Category, Brand, Season, Color, Gender

class InventoryModelTestCase(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Cat")
        self.brand = Brand.objects.create(name="Brand")
        self.season = Season.objects.create(name="Season")
        self.color = Color.objects.create(name="Color", code="#000000")
        self.gender = Gender.objects.create(name="Unisex")
        self.product = Product.objects.create(
            name="Prod", category=self.category, brand=self.brand, season=self.season,
            color=self.color, gender=self.gender, sale_price=100, cost_price=50
        )
        self.inventory = Inventory.objects.get(product=self.product)

    def test_str_method(self):
        self.assertEqual(str(self.inventory), f"{self.product} - {self.inventory.quantity}")

    def test_update_quantity(self):
        self.assertEqual(self.inventory.quantity, 0)
        self.inventory.update_quantity(10)
        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.quantity, 10)
        
        self.inventory.update_quantity(-5)
        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.quantity, 5)

from django.test import TestCase
from inventory.models import Inventory
from products.models import Product, Category, Brand, Season, Color, Gender
from utils.tests import TenantTestCase, create_test_branch

class InventoryModelTestCase(TenantTestCase, TestCase):
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

    def test_create_branch_stock_signal(self):
        """Test that creating a branch generates inventory for existing products."""
        from core.models import Branch
        new_branch = Branch.objects.create(company=self.company, name="New Signal Branch", code="NB-SIG")
        self.assertTrue(Inventory.objects.filter(product=self.product, branch=new_branch).exists())

    def test_stock_adjustment_request_str(self):
        from inventory.models import StockAdjustmentRequest
        adj = StockAdjustmentRequest.objects.create(
            company=self.company,
            branch=self.branch,
            product=self.product,
            adjustment_type=StockAdjustmentRequest.AdjustmentType.REDUCTION,
            quantity=5,
            reason="Test"
        )
        self.assertEqual(str(adj), f"{adj.adjustment_type} - {self.product} - {adj.quantity} ({adj.status})")

    def test_stock_movement_str(self):
        from inventory.models import StockMovement
        mov = StockMovement.objects.create(
            company=self.company,
            branch=self.branch,
            product=self.product,
            movement_type=StockMovement.MovementType.CORRECTION,
            previous_quantity=10,
            new_quantity=15,
            quantity_change=5
        )
        self.assertEqual(str(mov), f"{mov.movement_type} - {self.product} - {mov.quantity_change} ({mov.created_at})")

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from inventory.models import Inventory
from products.models import Product, Category, Brand, Season, Color, Gender

User = get_user_model()

class InventoryViewSetTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)
        
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
        self.url = reverse('inventory-list')

    def test_list_inventory(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_update_quantity_addition(self):
        url = reverse('inventory-update-quantity', args=[self.inventory.id])
        data = {"operation": "addition", "quantity": 10}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.quantity, 10)

    def test_update_quantity_subtraction(self):
        self.inventory.quantity = 20
        self.inventory.save()
        
        url = reverse('inventory-update-quantity', args=[self.inventory.id])
        data = {"operation": "subtraction", "quantity": 5}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.quantity, 15)

    def test_search_inventory(self):
        # Create another product and inventory
        other_product = Product.objects.create(
            name="Zapatillas", category=self.category, brand=self.brand, season=self.season,
            color=self.color, gender=self.gender, sale_price=200, cost_price=100,
            internal_code="ZAP123"
        )
        # Inventory is auto-created by signal? No, checking models... 
        # Product model has 'inventory: Inventory' type hint but no auto-creation logic visible in models.py shown.
        # But Inventory has OneToOne to Product.
        # Let's check if Inventory is created automatically. 
        # In setUp: self.inventory = Inventory.objects.get(product=self.product) implies it might be created automatically 
        # OR created in Product creation? 
        # Wait, looking at Product model: `inventory: Inventory` is just a type hint.
        # Looking at Inventory model: `product = OneToOneField`.
        # If it's not auto-created, I need to create it.
        # Let's assume for now I need to create it if it doesn't exist.
        # But in setUp `Inventory.objects.get` succeeds, so it MUST be created somewhere.
        # Maybe a signal in `inventory/apps.py` or `inventory/signals.py`?
        # I'll create it explicitly just in case, or check if it exists.
        if not Inventory.objects.filter(product=other_product).exists():
            Inventory.objects.create(product=other_product, quantity=5)
        
        # Search by product name
        response = self.client.get(self.url, {'search': 'Zapatillas'})
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['product']['name'], "Zapatillas")

        # Search by internal code
        response = self.client.get(self.url, {'search': 'ZAP123'})
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['product']['name'], "Zapatillas")

    def test_ordering_inventory(self):
        # Setup: 
        # Inv 1: "Prod" (Qty 0)
        # Inv 2: "AAA Product" (Qty 100)
        
        # Set Inv 1 to Qty 100, Inv 2 to Qty 0 to test quantity sorting against ID order
        self.inventory.quantity = 100
        self.inventory.save()
        
        other_product = Product.objects.create(
            name="AAA Product", category=self.category, brand=self.brand, season=self.season,
            color=self.color, gender=self.gender, sale_price=200, cost_price=100
        )
        if not Inventory.objects.filter(product=other_product).exists():
            inv2 = Inventory.objects.create(product=other_product, quantity=0)
        else:
            inv2 = Inventory.objects.get(product=other_product)
            inv2.quantity = 0
            inv2.save()
            
        # Verify IDs: Inv1 < Inv2
        self.assertLess(self.inventory.id, inv2.id)
        
        # 1. Test Quantity Ascending (Should be Inv 2 (0), then Inv 1 (100))
        # This is REVERSE ID order. If this works, sorting works.
        response = self.client.get(self.url, {'ordering': 'quantity'})
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(response.data['results'][0]['quantity'], 0)
        self.assertEqual(response.data['results'][1]['quantity'], 100)
        
        # 2. Test Name Ascending (Should be Inv 2 ("AAA"), then Inv 1 ("Prod"))
        # This is also REVERSE ID order.
        response = self.client.get(self.url, {'ordering': 'product__name'})
        self.assertEqual(response.data['results'][0]['product']['name'], "AAA Product")
        self.assertEqual(response.data['results'][1]['product']['name'], "Prod")

    def test_update_quantity_errors(self):
        url = reverse('inventory-update-quantity', args=[self.inventory.id])
        
        # Test invalid quantity (negative)
        data = {"operation": "addition", "quantity": -5}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Invalid quantity')

        # Test invalid quantity (missing/zero)
        data = {"operation": "addition", "quantity": 0}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test invalid operation
        data = {"operation": "multiply", "quantity": 10}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Invalid operation')

    def test_low_stock(self):
        # self.inventory has 0 quantity, should be in low stock
        url = reverse('inventory-low-stock')
        response = self.client.get(url)  # Default threshold is 5
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], self.product.name)

        # Update quantity to be above threshold
        self.inventory.quantity = 10
        self.inventory.save()
        
        response = self.client.get(url)
        self.assertEqual(len(response.data), 0)

        # Test custom threshold
        response = self.client.get(url, {'threshold': 15})
        self.assertEqual(len(response.data), 1)

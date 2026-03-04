from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from inventory.models import Inventory
from products.models import Product, Category, Brand, Season, Color, Gender
from utils.tests import TenantTestCase, create_test_branch

class InventoryViewSetTestCase(TenantTestCase, APITestCase):
    def setUp(self):
        super().setUp()
        self.client.force_authenticate(user=self.user)
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
        self.url = reverse('inventory-list')

    def test_list_inventory(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_list_inventory_with_branch_filter(self):
        response = self.client.get(self.url, {'branch': self.branch.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_list_inventory_user_branch_filter(self):
        self.user.branch.add(self.branch)
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
        other_product = Product.objects.create(
            company=self.company,
            name="Zapatillas", category=self.category, brand=self.brand, season=self.season,
            color=self.color, gender=self.gender, sale_price=200, cost_price=100,
            internal_code="ZAP123"
        )
        
        response = self.client.get(self.url, {'search': 'Zapatillas'})
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['product']['name'], "Zapatillas")

        response = self.client.get(self.url, {'search': 'ZAP123'})
        self.assertEqual(len(response.data['results']), 1)

    def test_ordering_inventory(self):
        self.inventory.quantity = 100
        self.inventory.save()
        
        other_product = Product.objects.create(
            company=self.company,
            name="AAA Product", category=self.category, brand=self.brand, season=self.season,
            color=self.color, gender=self.gender, sale_price=200, cost_price=100
        )
        inv2 = Inventory.objects.get(product=other_product)
        inv2.quantity = 0
        inv2.save()
            
        self.assertLess(self.inventory.id, inv2.id)
        
        response = self.client.get(self.url, {'ordering': 'quantity'})
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(response.data['results'][0]['quantity'], 0)
        self.assertEqual(response.data['results'][1]['quantity'], 100)
        
        response = self.client.get(self.url, {'ordering': 'product__name'})
        self.assertEqual(response.data['results'][0]['product']['name'], "AAA Product")
        self.assertEqual(response.data['results'][1]['product']['name'], "Prod")

    def test_update_quantity_errors(self):
        url = reverse('inventory-update-quantity', args=[self.inventory.id])
        
        data = {"operation": "addition", "quantity": -5}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Invalid quantity')

        data = {"operation": "addition", "quantity": 0}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = {"operation": "multiply", "quantity": 10}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Invalid operation')

    def test_low_stock(self):
        url = reverse('inventory-low-stock')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], self.product.name)

        self.inventory.quantity = 10
        self.inventory.save()
        
        response = self.client.get(url)
        self.assertEqual(len(response.data), 0)

        response = self.client.get(url, {'threshold': 15})
        self.assertEqual(len(response.data), 1)

    def test_other_branches_availability(self):
        """Test getting availability across other branches excluding the ones of the user."""
        
        # Create a second branch
        from core.models import Branch
        branch2 = Branch.objects.create(company=self.company, name="Branch 2", code="BR2")
        
        # Branch 2 should automatically have 0-stock inventory for self.product per our previous signals
        inv2 = Inventory.objects.get(product=self.product, branch=branch2)
        inv2.quantity = 15
        inv2.save()
        
        url = reverse('inventory-other-branches', args=[self.inventory.id])
        
        # Scenario 1: User belongs to Branch 1
        self.user.branch.add(self.branch)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return Branch 2's inventory but NOT Branch 1's
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['branch'], branch2.id)
        self.assertEqual(response.data[0]['quantity'], 15)
        
        # Scenario 2: User has NO branch assigned
        self.user.branch.clear()
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should exclude the branch of the item being queried (Branch 1)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['branch'], branch2.id)
        self.assertEqual(response.data[0]['quantity'], 15)

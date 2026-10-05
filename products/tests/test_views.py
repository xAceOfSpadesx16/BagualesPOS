from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from products.models import Product, Category, Brand, Season, Color, Gender

User = get_user_model()

class ProductViewSetTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)
        
        self.category = Category.objects.create(name="Pantalones")
        self.brand = Brand.objects.create(name="Adidas")
        self.season = Season.objects.create(name="Invierno")
        self.color = Color.objects.create(name="Azul", code="#0000FF")
        self.gender = Gender.objects.create(name="Unisex")
        
        self.product = Product.objects.create(
            name="Pantalon Adidas",
            category=self.category,
            brand=self.brand,
            season=self.season,
            color=self.color,
            gender=self.gender,
            sale_price=2000,
            cost_price=1000
        )
        self.url = reverse('product-list')

    def test_list_products(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_create_product(self):
        data = {
            "name": "Nuevo Producto",
            "category": self.category.id,
            "brand": self.brand.id,
            "season": self.season.id,
            "color": self.color.id,
            "gender": self.gender.id,
            "sale_price": 3000,
            "cost_price": 1500,
            "numeric_size": 42
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 2)

    def test_soft_delete_product(self):
        url = reverse('product-detail', args=[self.product.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.product.refresh_from_db()
        self.assertTrue(self.product.is_deleted)

    def test_filter_products(self):
        # Create another product with different attributes
        other_category = Category.objects.create(name="Remeras")
        Product.objects.create(
            name="Remera Nike",
            category=other_category,
            brand=self.brand,
            season=self.season,
            color=self.color,
            gender=self.gender,
            sale_price=1500,
            cost_price=800
        )
        
        # Filter by category
        response = self.client.get(self.url, {'category': self.category.id})
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], "Pantalon Adidas")

    def test_search_products(self):
        # Create another product
        Product.objects.create(
            name="Zapatillas Puma",
            category=self.category,
            brand=self.brand,
            season=self.season,
            color=self.color,
            gender=self.gender,
            sale_price=5000,
            cost_price=3000,
            internal_code="PUMA123"
        )

        # Search by name
        response = self.client.get(self.url, {'search': 'Adidas'})
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], "Pantalon Adidas")

        # Search by internal_code
        response = self.client.get(self.url, {'search': 'PUMA123'})
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], "Zapatillas Puma")

    def test_ordering_products(self):
        # Create another product with higher price
        Product.objects.create(
            name="Campera",
            category=self.category,
            brand=self.brand,
            season=self.season,
            color=self.color,
            gender=self.gender,
            sale_price=10000,
            cost_price=5000
        )

        # Order by sale_price ascending
        response = self.client.get(self.url, {'ordering': 'sale_price'})
        self.assertEqual(response.data['results'][0]['name'], "Pantalon Adidas") # 2000
        self.assertEqual(response.data['results'][1]['name'], "Campera") # 10000

        # Order by sale_price descending
        response = self.client.get(self.url, {'ordering': '-sale_price'})
        self.assertEqual(response.data['results'][0]['name'], "Campera")
        self.assertEqual(response.data['results'][1]['name'], "Pantalon Adidas")

    def test_retrieve_product(self):
        url = reverse('product-detail', args=[self.product.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Pantalon Adidas")
        # Should use ProductDetailSerializer, so check for a field specific to it if any, 
        # or just reliance on coverage reporting. 
        # ProductDetailSerializer has 'formatted_sale_price'
        self.assertIn('formatted_sale_price', response.data)

    def test_create_product_invalid(self):
        # Missing required fields
        data = {"name": "Invalid"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class CategoryViewSetTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='admin', password='password')
        self.client.force_authenticate(user=self.user)
        self.category = Category.objects.create(name="Test Category")
        self.list_url = reverse('category-list')
        self.detail_url = reverse('category-detail', args=[self.category.id])

    def test_list_categories(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should use CategoryListSerializer

    def test_create_category(self):
        data = {"name": "New Category"}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Should use CategoryWriteSerializer

    def test_update_category(self):
        data = {"name": "Updated Category"}
        response = self.client.put(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, "Updated Category")

    def test_retrieve_category(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should use CategoryListSerializer (default in BaseViewSet)

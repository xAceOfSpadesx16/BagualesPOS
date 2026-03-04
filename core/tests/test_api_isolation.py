from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django_multitenant.utils import get_current_tenant, set_current_tenant
from core.models import Company
from products.models import Product, Category, Brand, Season, Color, Gender

User = get_user_model()

class APIEndToEndIsolationTestCase(APITestCase):
    """
    E2E Integration tests that verify the TenantMiddleware correctly isolates 
    data per tenant purely through HTTP requests.
    
    IMPORTANT: These tests DO NOT use TenantTestCase or manually set the tenant 
    context via set_current_tenant() before making requests. This ensures the 
    actual middleware is processing the request and extracting the tenant from 
    the authenticated user.
    """

    def setUp(self):
        # We must explicitly clean the tenant context just in case another test leaked it
        set_current_tenant(None)

        # 1. Create Company A and User A
        self.company_a = Company.objects.create(name="Company A", tax_id="111")
        
        # When creating objects outside of a request, we MUST set the tenant manually 
        # so the objects belong to the correct company in the DB.
        set_current_tenant(self.company_a)
        
        self.user_a = User.objects.create_user(
            username="user_a",
            password="password",
            company=self.company_a
        )
        
        # Create some data for Company A
        category_a = Category.objects.create(company=self.company_a, name="Cat A")
        brand_a = Brand.objects.create(company=self.company_a, name="Brand A")
        season = Season.objects.create(name="All Seasons")  # Global
        color = Color.objects.create(name="Red", code="#FF0000")  # Global
        gender = Gender.objects.create(name="Unisex")  # Global

        self.product_a = Product.objects.create(
            company=self.company_a,
            name="Product A",
            category=category_a,
            brand=brand_a,
            season=season,
            color=color,
            gender=gender,
            sale_price="100.00",
            cost_price="50.00"
        )

        set_current_tenant(None)

        # 2. Create Company B and User B
        self.company_b = Company.objects.create(name="Company B", tax_id="222")
        
        set_current_tenant(self.company_b)
        
        self.user_b = User.objects.create_user(
            username="user_b",
            password="password",
            company=self.company_b
        )
        
        # Create some data for Company B
        category_b = Category.objects.create(company=self.company_b, name="Cat B")
        brand_b = Brand.objects.create(company=self.company_b, name="Brand B")

        self.product_b = Product.objects.create(
            company=self.company_b,
            name="Product B",
            category=category_b,
            brand=brand_b,
            season=season, # Shared reference
            color=color,   # Shared reference
            gender=gender, # Shared reference
            sale_price="200.00",
            cost_price="100.00"
        )
        
        # Clean up before running actual API tests
        set_current_tenant(None)
        
        self.products_url = reverse('product-list')

    def test_tenant_middleware_filters_products_for_user_a(self):
        """Verify User A only sees Company A's products"""
        # Ensure no tenant is set before the request
        self.assertIsNone(get_current_tenant())

        # Authenticate using JWT to simulate a real API client
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(self.user_a)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Make the request. The middleware SHOULD kick in here.
        response = self.client.get(self.products_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should only return 1 product (Product A)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], "Product A")
        
        # Check TenantContext was cleared after the request finished
        self.assertIsNone(get_current_tenant())

    def test_tenant_middleware_filters_products_for_user_b(self):
        """Verify User B only sees Company B's products"""
        self.assertIsNone(get_current_tenant())

        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(self.user_b)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        response = self.client.get(self.products_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], "Product B")

    def test_tenant_middleware_prevents_user_a_from_fetching_product_b(self):
        """Verify User A cannot directly fetch Product B by ID"""
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(self.user_a)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        detail_url = reverse('product-detail', args=[self.product_b.id])
        response = self.client.get(detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthenticated_request_handling(self):
        """Verify unauthenticated requests don't leak data"""
        self.client.credentials()
        
        response = self.client.get(self.products_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_post_creation_is_isolated(self):
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(self.user_a)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        category_a = Category.objects.filter(company=self.company_a).first()
        brand_a = Brand.objects.filter(company=self.company_a).first()
        season = Season.objects.first()
        color = Color.objects.first()
        gender = Gender.objects.first()
        
        data = {
            "name": "New Product A",
            "category": category_a.id,
            "brand": brand_a.id,
            "season": season.id,
            "color": color.id,
            "gender": gender.id,
            "sale_price": "300.00",
            "cost_price": "150.00",
            "numeric_size": 42
        }
        
        response = self.client.post(self.products_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        set_current_tenant(self.company_a)
        product_count_a = Product.objects.count()
        self.assertEqual(product_count_a, 2)
        
        set_current_tenant(self.company_b)
        product_count_b = Product.objects.count()
        self.assertEqual(product_count_b, 1)
        
        set_current_tenant(None)


from django.test import TestCase
from products.models import Product, Category, Brand, Season, Color, Gender
from products.serializers import ProductListSerializer, ProductDetailSerializer
from utils.tests import TenantTestCase

class ProductSerializerTestCase(TenantTestCase, TestCase):
    def setUp(self):
        super().setUp()
        self.category = Category.objects.create(company=self.company, name="Remeras")
        self.brand = Brand.objects.create(company=self.company, name="Nike")
        self.season = Season.objects.create(name="Verano")
        self.color = Color.objects.create(name="Rojo", code="#FF0000")
        self.gender = Gender.objects.create(name="Unisex")
        self.product = Product.objects.create(
            company=self.company,
            name="Remera Nike",
            category=self.category,
            brand=self.brand,
            season=self.season,
            color=self.color,
            gender=self.gender,
            sale_price=1000,
            cost_price=500
        )

    def test_list_serializer(self):
        serializer = ProductListSerializer(self.product)
        data = serializer.data
        self.assertEqual(data['name'], "Remera Nike")

    def test_detail_serializer(self):
        serializer = ProductDetailSerializer(self.product)
        data = serializer.data
        self.assertEqual(data['name'], "Remera Nike")
        self.assertEqual(data['sale_price'], '1000.00')

    def test_validation_errors(self):
        from products.serializers import ProductCreateUpdateSerializer
        
        # Test cost_price >= sale_price
        data = {
            "name": "Bad Price",
            "category": self.category.id,
            "brand": self.brand.id,
            "season": self.season.id,
            "color": self.color.id,
            "gender": self.gender.id,
            "sale_price": "100.00",
            "cost_price": "100.00", # Equal
            "numeric_size": 42
        }
        serializer = ProductCreateUpdateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('sale_price', serializer.errors)
        
        # Test missing size
        data['sale_price'] = "200.00" # Fix price
        del data['numeric_size']
        serializer = ProductCreateUpdateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        # The error is non-field error because it's in validate()
        self.assertTrue(serializer.errors.get('non_field_errors'))
        
        # Test double size
        data['numeric_size'] = 42
        
        # Create LetterSize for test
        from products.models import LetterSize
        ls = LetterSize.objects.create(name="L", short_name="L")
        data['letter_size'] = ls.id
        
        serializer = ProductCreateUpdateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertTrue(serializer.errors.get('non_field_errors'))

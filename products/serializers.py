from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from .models import (
    Product,
    Brand,
    Category,
    Subcategory,
    Color,
    Gender,
    LetterSize,
    Materials,
    Season,
    Supplier,
    PriceHistory,
)

# "List" Serializers for Read-Only Representations (e.g., in list views)

class CategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class SubcategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subcategory
        fields = ['id', 'name']

class SeasonListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Season
        fields = ['id', 'name']

class ColorListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ['id', 'name', 'code']

class GenderListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gender
        fields = ['id', 'name']

class LetterSizeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = LetterSize
        fields = ['id', 'name']

class MaterialsListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Materials
        fields = ['id', 'name']

class SupplierListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['id', 'name']

class BrandListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name']

# "Write" Serializers for Create/Update Operations

class CategoryWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class SubcategoryWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subcategory
        fields = '__all__'

class SeasonWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Season
        fields = '__all__'

class ColorWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = '__all__'

class GenderWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gender
        fields = '__all__'

class LetterSizeWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = LetterSize
        fields = '__all__'

class MaterialsWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Materials
        fields = '__all__'

class SupplierWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'

class BrandWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = '__all__'

# Product Serializers

class ProductListSerializer(serializers.ModelSerializer):
    brand = BrandListSerializer()
    category = CategoryListSerializer()
    sale_price = serializers.CharField(source='formatted_sale_price')

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'brand',
            'category',
            'sale_price',
            'is_active',
        ]

class ProductDetailSerializer(serializers.ModelSerializer):
    gender = GenderListSerializer()
    letter_size = LetterSizeListSerializer()
    material = MaterialsListSerializer()
    color = ColorListSerializer()
    brand = BrandListSerializer()
    category = CategoryListSerializer()
    subcategories = SubcategoryListSerializer(many=True)
    season = SeasonListSerializer()
    formatted_cost_price = serializers.SerializerMethodField()
    formatted_sale_price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'numeric_size', 'cost_price', 'formatted_cost_price',
            'sale_price', 'formatted_sale_price', 'internal_code', 'details',
            'image', 'is_active', 'gender', 'letter_size', 'material',
            'color', 'brand', 'category', 'subcategories', 'season',
            'created_at', 'updated_at', 'is_deleted', 'deleted_at',
        ]
        read_only_fields = [
            'internal_code', 'created_at', 'updated_at', 'is_deleted', 'deleted_at',
            'formatted_cost_price', 'formatted_sale_price'
        ]

    def get_formatted_cost_price(self, obj):
        return obj.formatted_cost_price

    def get_formatted_sale_price(self, obj):
        return obj.formatted_sale_price

class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'name', 'numeric_size', 'cost_price', 'sale_price', 'details',
            'image', 'is_active', 'gender', 'letter_size', 'material',
            'color', 'brand', 'category', 'subcategories', 'season',
        ]
        extra_kwargs = {
            'brand': {'required': True, 'allow_null': False},
            'category': {'required': True, 'allow_null': False},
            'gender': {'required': True, 'allow_null': False},
            'color': {'required': True, 'allow_null': False},
            'season': {'required': True, 'allow_null': False},
        }

    def validate(self, data):
        """
        - Check that cost_price is less than sale_price.
        - Check that either numeric_size or letter_size is provided, but not both.
        """
        if 'cost_price' in data and 'sale_price' in data:
            if data['cost_price'] >= data['sale_price']:
                raise serializers.ValidationError({
                    "sale_price": _("Sale price must be greater than cost price.")
                })

        if not data.get('numeric_size') and not data.get('letter_size'):
            raise serializers.ValidationError(
                _("Either numeric size or letter size is required.")
            )

        if data.get('numeric_size') and data.get('letter_size'):
            raise serializers.ValidationError(
                _("Provide either numeric size or letter size, not both.")
            )

        return data


class PriceHistorySerializer(serializers.ModelSerializer):
    changed_by_name = serializers.CharField(source='changed_by.get_full_name', read_only=True, default='')

    class Meta:
        model = PriceHistory
        fields = [
            'id', 'product', 'field', 'old_value', 'new_value',
            'change_percentage', 'reason', 'source',
            'changed_by', 'changed_by_name', 'created_at',
        ]
        read_only_fields = fields

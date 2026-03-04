from rest_framework import viewsets
from .models import (
    Product, Brand, Category, Subcategory, Color, Gender,
    LetterSize, Materials, Season, Supplier
)
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import (
    # Product
    ProductListSerializer,
    ProductDetailSerializer,
    ProductCreateUpdateSerializer,
    # Category
    CategoryListSerializer,
    CategoryWriteSerializer,
    # Subcategory
    SubcategoryListSerializer,
    SubcategoryWriteSerializer,
    # Season
    SeasonListSerializer,
    SeasonWriteSerializer,
    # Color
    ColorListSerializer,
    ColorWriteSerializer,
    # Gender
    GenderListSerializer,
    GenderWriteSerializer,
    # LetterSize
    LetterSizeListSerializer,
    LetterSizeWriteSerializer,
    # Materials
    MaterialsListSerializer,
    MaterialsWriteSerializer,
    # Supplier
    SupplierListSerializer,
    SupplierWriteSerializer,
    # Brand
    BrandListSerializer,
    BrandWriteSerializer,
)

class BaseViewSet(viewsets.ModelViewSet):
    """
    Base ViewSet to handle dynamic serializer selection.
    """
    list_serializer_class = None
    write_serializer_class = None

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return self.write_serializer_class
        return self.list_serializer_class

    def get_queryset(self):
        return self.queryset.model.objects.all()

class CategoryViewSet(BaseViewSet):
    queryset = Category.objects.all()
    list_serializer_class = CategoryListSerializer
    write_serializer_class = CategoryWriteSerializer

class SubcategoryViewSet(BaseViewSet):
    queryset = Subcategory.objects.all()
    list_serializer_class = SubcategoryListSerializer
    write_serializer_class = SubcategoryWriteSerializer

class SeasonViewSet(BaseViewSet):
    queryset = Season.objects.all()
    list_serializer_class = SeasonListSerializer
    write_serializer_class = SeasonWriteSerializer

class ColorViewSet(BaseViewSet):
    queryset = Color.objects.all()
    list_serializer_class = ColorListSerializer
    write_serializer_class = ColorWriteSerializer

class GenderViewSet(BaseViewSet):
    queryset = Gender.objects.all()
    list_serializer_class = GenderListSerializer
    write_serializer_class = GenderWriteSerializer

class LetterSizeViewSet(BaseViewSet):
    queryset = LetterSize.objects.all()
    list_serializer_class = LetterSizeListSerializer
    write_serializer_class = LetterSizeWriteSerializer

class MaterialsViewSet(BaseViewSet):
    queryset = Materials.objects.all()
    list_serializer_class = MaterialsListSerializer
    write_serializer_class = MaterialsWriteSerializer

class SupplierViewSet(BaseViewSet):
    queryset = Supplier.objects.all()
    list_serializer_class = SupplierListSerializer
    write_serializer_class = SupplierWriteSerializer

class BrandViewSet(BaseViewSet):
    queryset = Brand.objects.all()
    list_serializer_class = BrandListSerializer
    write_serializer_class = BrandWriteSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    list_serializer_class = ProductListSerializer
    detail_serializer_class = ProductDetailSerializer
    write_serializer_class = ProductCreateUpdateSerializer
    ordering = ['name', 'brand__name']
    
    def get_queryset(self):
        return Product.objects.all()


    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return ProductCreateUpdateSerializer
        return ProductDetailSerializer

    def perform_destroy(self, instance):
        instance.soft_delete()

    filterset_fields = ['category', 'brand', 'gender', 'season']
    search_fields = ['name', 'details', 'internal_code']
    ordering_fields = ['sale_price', 'name', 'created_at']
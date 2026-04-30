from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from .models import (
    Product, Brand, Category, Subcategory, Color, Gender,
    LetterSize, Materials, Season, Supplier, PriceHistory,
)
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import (
    # Product
    ProductListSerializer,
    ProductDetailSerializer,
    ProductCreateUpdateSerializer,
    # PriceHistory
    PriceHistorySerializer,
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

    @action(detail=True, methods=['get'], url_path='price-history')
    def price_history(self, request, pk=None):
        """GET /api/products/{id}/price-history/"""
        product = self.get_object()
        queryset = PriceHistory.objects.filter(product=product).select_related('changed_by')

        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        limit = int(request.query_params.get('limit', 50))

        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)

        serializer = PriceHistorySerializer(queryset[:limit], many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='bulk-update-prices')
    @transaction.atomic
    def bulk_update_prices(self, request):
        """
        POST /api/products/bulk-update-prices/
        Actualización masiva de precios (porcentaje o absoluto).
        """
        mode = request.data.get('mode')
        adjustment = request.data.get('adjustment')
        target_field = request.data.get('target_field', 'sale_price')
        product_ids = request.data.get('product_ids', [])
        filters = request.data.get('filters', {})
        round_to = int(request.data.get('round_to', 2))
        reason = request.data.get('reason', 'Bulk update')

        if mode not in ('percentage', 'absolute'):
            return Response(
                {'status': 400, 'message': "mode must be 'percentage' or 'absolute'"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if adjustment is None:
            return Response(
                {'status': 400, 'message': 'adjustment is required'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        adjustment = float(adjustment)
        queryset = self.get_queryset()
        if product_ids:
            queryset = queryset.filter(id__in=product_ids)
        if filters.get('category'):
            queryset = queryset.filter(category_id=filters['category'])
        if filters.get('brand'):
            queryset = queryset.filter(brand_id=filters['brand'])

        updated = []
        for product in queryset.select_related('company'):
            old_sale = product.sale_price
            old_cost = product.cost_price

            if target_field in ('sale_price', 'both'):
                if mode == 'percentage':
                    product.sale_price = round(old_sale * (1 + adjustment / 100), round_to)
                else:
                    product.sale_price = round(adjustment, round_to)

            if target_field in ('cost_price', 'both'):
                if mode == 'percentage':
                    product.cost_price = round(old_cost * (1 + adjustment / 100), round_to)
                else:
                    product.cost_price = round(adjustment, round_to)

            product.save()

            # Crear PriceHistory
            PriceHistory.objects.create(
                company=product.company,
                product=product,
                field=target_field if target_field != 'both' else 'sale_price',
                old_value=old_sale,
                new_value=product.sale_price,
                change_percentage=adjustment if mode == 'percentage' else None,
                reason=reason,
                source=PriceHistory.Source.BULK_UPDATE,
                changed_by=request.user,
            )

            if target_field in ('cost_price', 'both'):
                PriceHistory.objects.create(
                    company=product.company,
                    product=product,
                    field='cost_price',
                    old_value=old_cost,
                    new_value=product.cost_price,
                    change_percentage=adjustment if mode == 'percentage' else None,
                    reason=reason,
                    source=PriceHistory.Source.BULK_UPDATE,
                    changed_by=request.user,
                )

            updated.append({
                'id': product.id,
                'name': product.name,
                'old_sale_price': str(old_sale),
                'new_sale_price': str(product.sale_price),
                'old_cost_price': str(old_cost),
                'new_cost_price': str(product.cost_price),
            })

        return Response({
            'updated_count': len(updated),
            'products': updated,
        })
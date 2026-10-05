from django_filters import rest_framework as filters
from .models import StockAdjustmentRequest, StockMovement, StockTransfer


class StockAdjustmentRequestFilter(filters.FilterSet):
    """Filter for Stock Adjustment Requests"""

    status = filters.ChoiceFilter(choices=StockAdjustmentRequest.Status.choices)
    branch = filters.NumberFilter(field_name='branch__id')
    product = filters.NumberFilter(field_name='product__id')
    adjustment_type = filters.ChoiceFilter(choices=StockAdjustmentRequest.AdjustmentType.choices)
    date_from = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    date_to = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = StockAdjustmentRequest
        fields = ['status', 'branch', 'product', 'adjustment_type', 'date_from', 'date_to']


class StockMovementFilter(filters.FilterSet):
    """Filter for Stock Movements"""

    branch = filters.NumberFilter(field_name='branch__id')
    product = filters.NumberFilter(field_name='product__id')
    movement_type = filters.ChoiceFilter(choices=StockMovement.MovementType.choices)
    date_from = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    date_to = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = StockMovement
        fields = ['branch', 'product', 'movement_type', 'date_from', 'date_to']


class StockTransferFilter(filters.FilterSet):
    status = filters.CharFilter(field_name='status')
    origin_branch = filters.NumberFilter(field_name='origin_branch')
    destination_branch = filters.NumberFilter(field_name='destination_branch')
    date_from = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    date_to = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = StockTransfer
        fields = ['status', 'origin_branch', 'destination_branch']

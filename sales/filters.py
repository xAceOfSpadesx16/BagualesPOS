from django_filters import rest_framework as filters
from .models import Sale


class SaleFilter(filters.FilterSet):
    """Filter for Sale model with support for date ranges and branch filtering"""
    
    date_from = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    date_to = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    branch = filters.NumberFilter(field_name='branch__id')
    seller = filters.NumberFilter(field_name='seller__id')
    canceled = filters.BooleanFilter(field_name='canceled')
    
    class Meta:
        model = Sale
        fields = ['branch', 'date_from', 'date_to', 'seller', 'canceled', 'closed', 'pay_method', 'payment_status']

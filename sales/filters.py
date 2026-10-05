from django_filters import rest_framework as filters
from .models import Sale, Return


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


class ReturnFilter(filters.FilterSet):
    status = filters.CharFilter(field_name='status')
    branch = filters.NumberFilter(field_name='branch')
    sale = filters.NumberFilter(field_name='sale')
    reason_type = filters.CharFilter(field_name='reason_type')
    cash_session = filters.NumberFilter(field_name='cash_session')
    date_from = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    date_to = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = Return
        fields = ['status', 'branch', 'sale', 'reason_type', 'cash_session']

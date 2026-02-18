from rest_framework import viewsets
from sales.models import Sale
from sales.serializers import SaleSerializer

class RecordsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Sale.objects.select_related('client', 'pay_method').order_by('-id').all()
    serializer_class = SaleSerializer
    filterset_fields = ['closed', 'pay_method', 'seller']
    search_fields = ['client__name', 'client__last_name', 'client__dni']
    ordering_fields = ['created_at', 'total_amount']

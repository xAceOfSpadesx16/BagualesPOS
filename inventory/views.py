from rest_framework import viewsets, status
from django.utils.translation import gettext_lazy as _
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import F
from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from .models import Inventory
from .serializers import InventorySerializer

class InventoryViewSet(viewsets.ModelViewSet):
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    ordering = ['product__name', 'product__brand__name']
    search_fields = ['product__name', 'product__details', 'product__internal_code']
    ordering_fields = ['quantity', 'product__name']

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        
        # Filter by branch if provided in query params
        branch_id = self.request.query_params.get('branch')
        if branch_id:
            queryset = queryset.filter(branch_id=branch_id)
        # Otherwise filter by user's assigned branches
        elif hasattr(user, 'branch') and user.branch.exists():
            queryset = queryset.filter(branch__in=user.branch.all())
            
        return queryset

    @action(detail=True, methods=['post'])
    def update_quantity(self, request, pk=None):
        inventory = self.get_object()
        operation = request.data.get('operation')
        quantity = request.data.get('quantity')

        try:
            quantity = int(quantity)
            if quantity <= 0:
                raise ValueError
        except (TypeError, ValueError):
            return Response({'error': _('Invalid quantity')}, status=status.HTTP_400_BAD_REQUEST)

        if operation == 'addition':
            inventory.quantity = F('quantity') + quantity
        elif operation == 'subtraction':
            inventory.quantity = F('quantity') - quantity
        else:
            return Response({'error': _('Invalid operation')}, status=status.HTTP_400_BAD_REQUEST)
        
        inventory.save()
        inventory.refresh_from_db()
        return Response(self.get_serializer(inventory).data)

    @action(detail=False, methods=['get'], url_path='low-stock')
    def low_stock(self, request):
        """
        Returns items with low stock.
        """
        threshold = int(request.query_params.get('threshold', 5))
        low_stock_items = self.get_queryset().filter(quantity__lte=threshold)
        
        # We can use a custom serializer or the default one
        # For dashboard we need: product name, current stock, min stock (if we had it)
        # Currently Inventory model has quantity. Product has no min_stock field yet?
        # Let's check models. Assuming just quantity for now.
        
        data = []
        for item in low_stock_items:
            data.append({
                'id': item.id,
                'name': item.product.name,
                'stock': item.quantity,
                'min': 5 # Hardcoded for now as it seems not to be in model
            })
            
        return Response(data)

    @action(detail=True, methods=['get'], url_path='other-branches')
    def other_branches(self, request, pk=None):
        """
        Returns the availability of the product associated with this inventory
        in branches other than the one(s) the current user belongs to.
        """
        inventory = self.get_object()
        user = request.user
        
        # Base query for the same product
        qs = Inventory.objects.filter(product=inventory.product)
        
        # Exclude the user's branches if they have any
        if hasattr(user, 'branch') and user.branch.exists():
            qs = qs.exclude(branch__in=user.branch.all())
        else:
            # If user has no branches assigned (unlikely but possible), 
            # exclude the branch of the current inventory item
            qs = qs.exclude(branch=inventory.branch)
            
        # Serialize and return
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError as DRFValidationError
from django.utils.translation import gettext_lazy as _
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import F, Sum
from django.db import transaction
from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from utils.mixins import TenantViewSetMixin
from .models import Inventory, StockAdjustmentRequest, StockMovement, StockTransfer, StockTransferDetail
from .serializers import (
    InventorySerializer, StockAdjustmentRequestSerializer, StockMovementSerializer,
    StockTransferListSerializer, StockTransferCreateSerializer,
)
from .filters import StockAdjustmentRequestFilter, StockMovementFilter, StockTransferFilter

class InventoryViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    ordering = ['product__name', 'product__brand__name']
    search_fields = ['product__name', 'product__details', 'product__internal_code']
    ordering_fields = ['quantity', 'product__name']

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
    
    @action(detail=False, methods=['get'], url_path='stock-breakdown')
    def stock_breakdown(self, request):
        """
        Returns aggregated stock breakdown per product across all branches.
        Only available for General Admins (company owners or superusers).
        
        Query parameters:
        - product: Filter by product ID
        - branch: Filter by branch ID
        - low_stock: Show only products with total stock below threshold (default: 10)
        """
        user = request.user
        
        # Check if user is General Admin
        if not (user.is_superuser or hasattr(user, 'owned_company')):
            return Response(
                {'error': 'This endpoint is only available for General Administrators.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Start with base queryset (already filtered by company via get_queryset)
        queryset = self.get_queryset()
        
        # Apply filters
        product_id = request.query_params.get('product')
        branch_id = request.query_params.get('branch')
        low_stock_threshold = request.query_params.get('low_stock')
        
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        if branch_id:
            queryset = queryset.filter(branch_id=branch_id)
        
        # Aggregate by product
        from django.db.models import Count
        stock_data = queryset.values(
            'product__id',
            'product__name',
            'product__internal_code',
            'product__sale_price',
            'product__cost_price'
        ).annotate(
            total_stock=Sum('quantity'),
            branches_count=Count('branch', distinct=True)
        ).order_by('-total_stock')
        
        # Build detailed response with per-branch breakdown
        results = []
        for item in stock_data:
            product_id = item['product__id']
            
            # Get branch breakdown for this product
            branch_breakdown = queryset.filter(product_id=product_id).values(
                'branch__id',
                'branch__name',
                'branch__code',
                'quantity'
            ).order_by('branch__name')
            
            product_data = {
                'product_id': product_id,
                'product_name': item['product__name'],
                'product_code': item['product__internal_code'],
                'sale_price': float(item['product__sale_price']) if item['product__sale_price'] else 0,
                'cost_price': float(item['product__cost_price']) if item['product__cost_price'] else 0,
                'total_stock': item['total_stock'],
                'branches_count': item['branches_count'],
                'branches': list(branch_breakdown)
            }
            
            # Filter by low stock if requested
            if low_stock_threshold:
                try:
                    threshold = int(low_stock_threshold)
                    if item['total_stock'] <= threshold:
                        results.append(product_data)
                except ValueError:
                    pass
            else:
                results.append(product_data)
        
        return Response(results)


class StockAdjustmentRequestViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    """
    ViewSet for Stock Adjustment Requests.
    Branch managers can create requests, General Admins can approve/reject.
    """
    queryset = StockAdjustmentRequest.objects.all()
    serializer_class = StockAdjustmentRequestSerializer
    filterset_class = StockAdjustmentRequestFilter
    ordering = ['-created_at']

    def perform_create(self, serializer):
        """Auto-assign company, branch, user, and set status to PENDING"""
        user = self.request.user
        
        # Get user's first branch (assumes user has at least one)
        user_branch = user.branch.first() if user.branch.exists() else None
        
        if not user_branch:
            raise DRFValidationError({
                'detail': 'You must be assigned to a branch to create stock adjustment requests.'
            })
        
        serializer.save(
            company=user.company,
            branch=user_branch,
            requested_by=user,
            status=StockAdjustmentRequest.Status.PENDING
        )
    
    @action(detail=True, methods=['post'])
    @transaction.atomic
    def approve(self, request, pk=None):
        """
        Approve a stock adjustment request.
        Only General Admins can approve.
        """
        user = request.user
        
        # Check if user is General Admin
        if not (user.is_superuser or hasattr(user, 'owned_company')):
            return Response(
                {'error': 'Only General Administrators can approve stock adjustment requests.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        adjustment = self.get_object()
        
        # Validate status
        if adjustment.status != StockAdjustmentRequest.Status.PENDING:
            return Response(
                {'error': f'Cannot approve request with status: {adjustment.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get or create inventory
        try:
            inventory = Inventory.objects.select_for_update().get(
                product=adjustment.product,
                branch=adjustment.branch
            )
        except Inventory.DoesNotExist:
            return Response(
                {'error': 'Inventory record not found for this product and branch.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate quantity for reductions
        if adjustment.adjustment_type == StockAdjustmentRequest.AdjustmentType.REDUCTION:
            if inventory.quantity < abs(adjustment.quantity):
                return Response(
                    {'error': f'Insufficient stock. Available: {inventory.quantity}, Requested: {abs(adjustment.quantity)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Store previous quantity
        previous_quantity = inventory.quantity
        
        # Apply adjustment based on type
        if adjustment.adjustment_type == StockAdjustmentRequest.AdjustmentType.REDUCTION:
            inventory.quantity -= abs(adjustment.quantity)
        elif adjustment.adjustment_type == StockAdjustmentRequest.AdjustmentType.ADDITION:
            inventory.quantity += abs(adjustment.quantity)
        elif adjustment.adjustment_type == StockAdjustmentRequest.AdjustmentType.CORRECTION:
            inventory.quantity = adjustment.quantity
        
        inventory.save()
        
        # Create StockMovement record
        StockMovement.objects.create(
            company=adjustment.company,
            branch=adjustment.branch,
            product=adjustment.product,
            movement_type=StockMovement.MovementType.ADJUSTMENT,
            previous_quantity=previous_quantity,
            new_quantity=inventory.quantity,
            quantity_change=inventory.quantity - previous_quantity,
            reference_id=adjustment.id,
            reference_model='StockAdjustmentRequest',
            notes=f'Approved adjustment: {adjustment.reason}',
            created_by=user
        )
        
        # Update adjustment status
        adjustment.status = StockAdjustmentRequest.Status.APPROVED
        adjustment.approved_by = user
        adjustment.save()
        
        return Response(self.get_serializer(adjustment).data)
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """
        Reject a stock adjustment request.
        Only General Admins can reject.
        """
        user = request.user
        
        # Check if user is General Admin
        if not (user.is_superuser or hasattr(user, 'owned_company')):
            return Response(
                {'error': 'Only General Administrators can reject stock adjustment requests.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        adjustment = self.get_object()
        
        # Validate status
        if adjustment.status != StockAdjustmentRequest.Status.PENDING:
            return Response(
                {'error': f'Cannot reject request with status: {adjustment.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get rejection note from request data
        rejection_note = request.data.get('rejection_note', '')
        
        # Update adjustment status
        adjustment.status = StockAdjustmentRequest.Status.REJECTED
        adjustment.approved_by = user
        adjustment.rejection_note = rejection_note
        adjustment.save()
        
        return Response(self.get_serializer(adjustment).data)


class StockMovementViewSet(TenantViewSetMixin, viewsets.ReadOnlyModelViewSet):
    """Read-only ViewSet for Stock Movements (audit log)."""
    queryset = StockMovement.objects.all()
    serializer_class = StockMovementSerializer
    filterset_class = StockMovementFilter
    ordering = ['-created_at']


class StockTransferViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    """ViewSet para gestionar transferencias de stock entre sucursales."""
    queryset = StockTransfer.objects.select_related(
        'origin_branch', 'destination_branch', 'requested_by', 'approved_by'
    ).prefetch_related('details').order_by('-created_at')

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = StockTransferFilter
    ordering_fields = ['created_at', 'status']

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return StockTransferCreateSerializer
        return StockTransferListSerializer

    def perform_create(self, serializer):
        serializer.save(
            company=self.get_user_company(),
            requested_by=self.request.user,
        )

    @action(detail=True, methods=['post'])
    @transaction.atomic
    def approve(self, request, pk=None):
        """Aprueba transferencia: extrae stock de origen y pasa a IN_TRANSIT."""
        user = request.user
        if not (user.is_superuser or hasattr(user, 'owned_company')):
            return Response(
                {'status': 403, 'message': 'Only administrators can approve transfers.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        transfer = self.get_object()
        if transfer.status != StockTransfer.Status.PENDING:
            return Response(
                {'status': 400, 'message': f'Cannot approve transfer with status: {transfer.status}'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        for detail in transfer.details.select_related('product'):
            try:
                inventory = Inventory.objects.select_for_update().get(
                    product=detail.product, branch=transfer.origin_branch
                )
            except Inventory.DoesNotExist:
                return Response(
                    {'status': 400, 'message': f'No inventory for {detail.product} in origin branch.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if inventory.quantity < detail.quantity:
                return Response(
                    {'status': 400, 'message': f'Insufficient stock for {detail.product}. Available: {inventory.quantity}'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            detail.origin_stock_before = inventory.quantity
            inventory.quantity -= detail.quantity
            inventory.save()
            detail.origin_stock_after = inventory.quantity
            detail.save()

            StockMovement.objects.create(
                company=transfer.company,
                branch=transfer.origin_branch,
                product=detail.product,
                movement_type=StockMovement.MovementType.TRANSFER,
                previous_quantity=detail.origin_stock_before,
                new_quantity=inventory.quantity,
                quantity_change=-detail.quantity,
                reference_id=transfer.id,
                reference_model='StockTransfer',
                notes=f'Transfer #{transfer.id} to {transfer.destination_branch.name}',
                created_by=user,
            )

        transfer.status = StockTransfer.Status.IN_TRANSIT
        transfer.approved_by = user
        transfer.save()
        return Response(StockTransferListSerializer(transfer).data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Rechaza transferencia."""
        user = request.user
        if not (user.is_superuser or hasattr(user, 'owned_company')):
            return Response(
                {'status': 403, 'message': 'Only administrators can reject transfers.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        transfer = self.get_object()
        if transfer.status != StockTransfer.Status.PENDING:
            return Response(
                {'status': 400, 'message': f'Cannot reject transfer with status: {transfer.status}'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        transfer.status = StockTransfer.Status.REJECTED
        transfer.approved_by = user
        transfer.rejection_note = request.data.get('rejection_note', '')
        transfer.save()
        return Response(StockTransferListSerializer(transfer).data)

    @action(detail=True, methods=['post'])
    @transaction.atomic
    def complete(self, request, pk=None):
        """Completa transferencia: suma stock en destino."""
        transfer = self.get_object()
        if transfer.status != StockTransfer.Status.IN_TRANSIT:
            return Response(
                {'status': 400, 'message': 'Transfer must be in transit to complete.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        for detail in transfer.details.select_related('product'):
            inventory, _ = Inventory.objects.select_for_update().get_or_create(
                product=detail.product,
                branch=transfer.destination_branch,
                defaults={
                    'company': transfer.company,
                    'quantity': 0,
                },
            )
            previous_qty = inventory.quantity
            inventory.quantity += detail.quantity
            inventory.save()

            StockMovement.objects.create(
                company=transfer.company,
                branch=transfer.destination_branch,
                product=detail.product,
                movement_type=StockMovement.MovementType.TRANSFER,
                previous_quantity=previous_qty,
                new_quantity=inventory.quantity,
                quantity_change=detail.quantity,
                reference_id=transfer.id,
                reference_model='StockTransfer',
                notes=f'Transfer #{transfer.id} from {transfer.origin_branch.name}',
                created_by=request.user,
            )

        transfer.status = StockTransfer.Status.COMPLETED
        transfer.save()
        return Response(StockTransferListSerializer(transfer).data)

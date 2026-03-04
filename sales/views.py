from decimal import Decimal
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError as DRFValidationError
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import Sum, Count, Avg, F
from django.db.models.functions import TruncMonth, TruncDate
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone
import datetime

from cash.models import CashSession
from cash.choices import SessionStatus
from .models import Sale, SaleDetail, PayMethod
from .serializers import SaleSerializer, SaleDetailSerializer, PayMethodSerializer

class PayMethodViewSet(viewsets.ModelViewSet):
    queryset = PayMethod.objects.all()
    serializer_class = PayMethodSerializer

class SaleViewSet(viewsets.ModelViewSet):
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer

    def perform_create(self, serializer):
        """Create sale and auto-assign to active cash session"""
        # Get active cash session for current user
        active_session = CashSession.objects.filter(
            user=self.request.user,
            status=SessionStatus.OPEN
        ).first()
        
        if not active_session:
            raise DRFValidationError({
                'detail': 'Debe abrir una sesión de caja antes de crear ventas. '
                         'Use POST /api/cash/cash-sessions/open/ para abrir una sesión.'
            })
        
        # Auto-assign session and seller
        serializer.save(
            seller=self.request.user,
            cash_session=active_session
        )


    @action(detail=True, methods=['post'])
    @transaction.atomic
    def close(self, request, pk=None):
        """Close a sale after validation"""
        sale = self.get_object()
        
        # Validation: sale must have at least one detail
        if not sale.details.exists():
            return Response(
                {'error': 'Cannot close a sale without items'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Set payment method if provided
        pay_method_id = request.data.get('pay_method')
        if pay_method_id:
            sale.pay_method_id = pay_method_id
        
        # If it's a credit sale, validate customer account
        if sale.client and hasattr(sale.client, 'customer_account'):
            customer_account = sale.client.customer_account
            
            # Check if account is active
            if not customer_account.active:
                return Response(
                    {'error': 'Customer account is not active'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check credit limit if applicable
            if customer_account.credit_limit is not None:
                current_balance = customer_account.balance
                future_balance = current_balance - sale.total_amount  # Debit reduces balance
                max_debt = customer_account.credit_limit * Decimal('-1')
                
                if future_balance < max_debt:
                    return Response({
                        'error': f'Credit limit exceeded. Available credit: {customer_account.credit_limit + current_balance}'
                    }, status=status.HTTP_400_BAD_REQUEST)
        
        # Close the sale with full model validation
        sale.closed = True
        try:
            sale.full_clean()
        except DjangoValidationError as e:
            return Response(
                {'error': e.message_dict if hasattr(e, 'message_dict') else e.messages},
                status=status.HTTP_400_BAD_REQUEST
            )
        sale.save()
        
        # The signals will handle:
        # - Creating CustomerBalanceRecord for credit sales
        # - Updating payment_status automatically
        
        return Response(self.get_serializer(sale).data)

    @action(detail=True, methods=['post'])
    @transaction.atomic
    def cancel(self, request, pk=None):
        """Cancel a sale and restore stock for all its items"""
        sale = self.get_object()

        if sale.canceled:
            return Response(
                {'error': 'Sale is already canceled'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Restore stock for each detail
        from inventory.models import Inventory
        if sale.branch:
            for detail in sale.details.select_related('product').all():
                if detail.product:
                    try:
                        stock = Inventory.objects.select_for_update().get(
                            product=detail.product, branch=sale.branch
                        )
                        stock.quantity += detail.quantity
                        stock.save()
                    except Inventory.DoesNotExist:
                        pass

        sale.canceled = True
        sale.save()

        return Response(self.get_serializer(sale).data)

    filterset_fields = ['closed', 'pay_method', 'seller', 'payment_status', 'canceled']
    search_fields = ['client__name', 'client__last_name', 'client__dni']
    ordering_fields = ['created_at', 'total_amount']

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Returns a summary of sales metrics.
        """
        total_sales = Sale.objects.filter(closed=True, canceled=False).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        total_transactions = Sale.objects.filter(closed=True, canceled=False).count()
        average_ticket = Sale.objects.filter(closed=True, canceled=False).aggregate(Avg('total_amount'))['total_amount__avg'] or 0
        total_products_sold = SaleDetail.objects.filter(order__closed=True, order__canceled=False).aggregate(Sum('quantity'))['quantity__sum'] or 0

        return Response({
            'total_sales': total_sales,
            'total_transactions': total_transactions,
            'average_ticket': average_ticket,
            'total_products_sold': total_products_sold
        })

    @action(detail=False, methods=['get'], url_path='top-products')
    def top_products(self, request):
        """
        Returns the top selling products.
        """
        limit = int(request.query_params.get('limit', 5))
        
        top_products = SaleDetail.objects.filter(order__closed=True, order__canceled=False).values(
            'product__name'
        ).annotate(
            product_name=F('product__name'),
            total_quantity=Sum('quantity'),
            total_revenue=Sum(F('quantity') * F('sale_price'))
        ).order_by('-total_quantity')[:limit]

        return Response(top_products)

    @action(detail=False, methods=['get'], url_path='sales-by-category')
    def sales_by_category(self, request):
        """
        Returns sales grouped by category.
        """
        data = SaleDetail.objects.filter(order__closed=True, order__canceled=False).values(
            'product__category__name'
        ).annotate(
            name=F('product__category__name'),
            value=Sum(F('quantity') * F('sale_price'))
        ).order_by('-value')

        # Add colors dynamically or static mapping could be done in frontend
        # For now just return name and value
        return Response(data)

    @action(detail=False, methods=['get'], url_path='sales-by-day')
    def sales_by_day(self, request):
        """
        Returns sales grouped by day for the last 7 days.
        """
        end_date = timezone.now()
        start_date = end_date - datetime.timedelta(days=6)

        sales = Sale.objects.filter(
            closed=True,
            canceled=False,
            created_at__date__range=[start_date.date(), end_date.date()]
        ).annotate(
            day=TruncDate('created_at')
        ).values('day').annotate(
            ventas=Sum('total_amount'),
            productos=Sum('details__quantity')
        ).order_by('day')

        # Format for frontend
        formatted_data = []
        current = start_date.date()
        sales_dict = {s['day']: s for s in sales}

        while current <= end_date.date():
            s = sales_dict.get(current, {'ventas': 0, 'productos': 0})
            formatted_data.append({
                'day': current.strftime('%a'), # Mon, Tue, etc.
                'full_date': current.strftime('%Y-%m-%d'),
                'ventas': s['ventas'] or 0,
                'productos': s['productos'] or 0
            })
            current += datetime.timedelta(days=1)

        return Response(formatted_data)

    @action(detail=False, methods=['get'], url_path='sales-by-month')
    def sales_by_month(self, request):
        """
        Returns sales grouped by month for the last 6 months.
        """


        end_date = timezone.now()
        start_date = end_date - datetime.timedelta(days=30*5)

        sales = Sale.objects.filter(
            closed=True,
            canceled=False,
            created_at__date__gte=start_date.date()
        ).annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            ventas=Sum('total_amount'),
            transacciones=Count('id')
        ).order_by('month')

        formatted_data = []
        current = start_date.replace(day=1)
        sales_dict = {s['month'].date(): s for s in sales if s['month']}

        while current.date() <= end_date.date():
            # Adjust current to match TruncMonth result (first of month)
            month_key = current.date().replace(day=1)
            s = sales_dict.get(month_key, {'ventas': 0, 'transacciones': 0})
            
            formatted_data.append({
                'month': current.strftime('%b'), # Jan, Feb
                'full_date': current.strftime('%Y-%m'),
                'ventas': s['ventas'] or 0,
                'transacciones': s['transacciones'] or 0
            })
            current += datetime.timedelta(days=30)

        return Response(formatted_data)

class SaleDetailViewSet(viewsets.ModelViewSet):
    queryset = SaleDetail.objects.all()
    serializer_class = SaleDetailSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        product = serializer.validated_data['product']
        order = serializer.validated_data['order']
        quantity = serializer.validated_data.get('quantity', 1)

        # Check if product already exists in this sale
        existing_detail = SaleDetail.objects.filter(order=order, product=product).first()
        
        if existing_detail:
            existing_detail.quantity += quantity
            try:
                existing_detail.full_clean()
            except DjangoValidationError as e:
                raise DRFValidationError(
                    e.message_dict if hasattr(e, 'message_dict') else e.messages
                )
            existing_detail.save()
            return Response(self.get_serializer(existing_detail).data, status=status.HTTP_200_OK)
        
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

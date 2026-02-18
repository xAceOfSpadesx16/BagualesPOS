from rest_framework import viewsets, status
from django.utils.translation import gettext_lazy as _
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Client, CustomerAccount, CustomerBalanceRecord
from .serializers import (
    ClientSerializer, 
    CustomerAccountSerializer, 
    CustomerBalanceRecordSerializer
)

class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    ordering = ['name', 'last_name']

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset

    filterset_fields = ['is_deleted', 'chosen_billing_type']
    search_fields = ['name', 'last_name', 'dni', 'email', 'cuit']
    ordering_fields = ['name', 'last_name', 'created_at']

    def perform_destroy(self, instance):
        instance.soft_delete()

    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        client = self.get_object()
        client.restore()
        return Response({'status': _('client restored')}, status=status.HTTP_200_OK)

class CustomerAccountViewSet(viewsets.ModelViewSet):
    queryset = CustomerAccount.objects.all()
    serializer_class = CustomerAccountSerializer

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        account = self.get_object()
        account.deactivate()
        return Response({'status': _('account deactivated')}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Returns a summary of all customer accounts.
        """
        from django.db.models import Sum
        from decimal import Decimal
        
        active_accounts = CustomerAccount.objects.filter(active=True)
        
        # Calculate total credit limit
        total_credit_limit = active_accounts.aggregate(
            Sum('credit_limit')
        )['credit_limit__sum'] or Decimal('0.00')
        
        # Calculate current balance by iterating (balance is a property, not a field)
        current_balance = Decimal('0.00')
        for account in active_accounts:
            current_balance += account.balance
        
        # Available credit calculation:
        # If balance is positive, client has credit (overpaid)
        # If balance is negative, client owes money
        # Available = limit + balance (since negative balance reduces available)
        available_credit = total_credit_limit + current_balance
        
        # Get total debit and credit from balance records (effective only)
        total_debit = CustomerBalanceRecord.objects.effective().by_debit().total_amount()
        total_credit = CustomerBalanceRecord.objects.effective().by_credit().total_amount()

        return Response({
            'credit_limit': total_credit_limit,
            'current_balance': current_balance,
            'available_credit': available_credit,
            'total_debit': total_debit,
            'total_credit': total_credit
        })

class CustomerBalanceRecordViewSet(viewsets.ModelViewSet):
    queryset = CustomerBalanceRecord.objects.all()
    serializer_class = CustomerBalanceRecordSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.core.exceptions import ValidationError as DjangoValidationError
from decimal import Decimal

from .models import CashRegister, CashSession, CashMovement
from .serializers import (
    CashRegisterSerializer, CashSessionSerializer, CashSessionListSerializer,
    CashMovementSerializer, OpenCashSessionSerializer, CloseCashSessionSerializer
)
from .choices import SessionStatus, MovementType


class CashRegisterViewSet(viewsets.ModelViewSet):
    """ViewSet for CashRegister management (for admin frontend)"""
    queryset = CashRegister.objects.all()
    serializer_class = CashRegisterSerializer
    filterset_fields = ['is_active']
    search_fields = ['name', 'code', 'location']
    
    @action(detail=True, methods=['get'])
    def current_session(self, request, pk=None):
        """Get the current open session for this cash register"""
        cash_register = self.get_object()
        session = cash_register.current_session
        
        if not session:
            return Response(
                {'detail': 'No open session for this cash register'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = CashSessionSerializer(session)
        return Response(serializer.data)



class CashSessionViewSet(viewsets.ModelViewSet):
    queryset = CashSession.objects.all()
    serializer_class = CashSessionSerializer
    filterset_fields = ['status', 'cash_register', 'user']
    ordering_fields = ['opening_date', 'closing_date']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CashSessionListSerializer
        return CashSessionSerializer
    
    @action(detail=False, methods=['post'])
    def open(self, request):
        """Open a new cash session"""
        serializer = OpenCashSessionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        cash_register_id = serializer.validated_data['cash_register']
        opening_balance = serializer.validated_data['opening_balance']
        
        # Get cash register
        cash_register = get_object_or_404(CashRegister, pk=cash_register_id)
        
        # Check if cash register is active
        if not cash_register.is_active:
            return Response(
                {'error': 'Cash register is not active'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create session
        session = CashSession(
            cash_register=cash_register,
            user=request.user,
            opening_balance=opening_balance,
            status=SessionStatus.OPEN
        )
        
        # Validate
        try:
            session.full_clean()
        except DjangoValidationError as e:
            return Response(
                {'error': dict(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        session.save()
        
        # Create opening movement
        CashMovement.objects.create(
            cash_session=session,
            type=MovementType.OPENING,
            amount=opening_balance,
            reason='Opening balance',
            created_by=request.user
        )
        
        return Response(
            CashSessionSerializer(session).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        """Close a cash session"""
        session = self.get_object()
        
        # Validate session is open
        if session.status != SessionStatus.OPEN:
            return Response(
                {'error': 'Session is already closed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate user is the owner or admin
        if session.user != request.user and not request.user.is_staff:
            return Response(
                {'error': 'Only the session owner or admin can close this session'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get and validate data
        serializer = CloseCashSessionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        closing_balance = serializer.validated_data['closing_balance']
        notes = serializer.validated_data.get('notes', '')
        
        # Update session
        session.closing_balance = closing_balance
        session.closing_date = timezone.now()
        session.status = SessionStatus.CLOSED
        session.notes = notes
        
        try:
            session.full_clean()
        except DjangoValidationError as e:
            return Response(
                {'error': dict(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        session.save()
        
        # Create closing movement
        CashMovement.objects.create(
            cash_session=session,
            type=MovementType.CLOSING,
            amount=closing_balance,
            reason='Closing balance',
            created_by=request.user
        )
        
        return Response(CashSessionSerializer(session).data)
    
    @action(detail=False, methods=['get'])
    def my_active(self, request):
        """Get the active session for the current user"""
        session = CashSession.objects.filter(
            user=request.user,
            status=SessionStatus.OPEN
        ).first()
        
        if not session:
            return Response(
                {'detail': 'No active session for this user'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(CashSessionSerializer(session).data)
    
    @action(detail=True, methods=['get'])
    def sales(self, request, pk=None):
        """Get sales for this session"""
        from sales.serializers import SaleSerializer
        
        session = self.get_object()
        sales = session.sales.filter(closed=True, canceled=False)
        
        serializer = SaleSerializer(sales, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def movements(self, request, pk=None):
        """Get movements for this session"""
        session = self.get_object()
        movements = session.movements.all()
        
        serializer = CashMovementSerializer(movements, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        """Get detailed summary of the session"""
        session = self.get_object()
        
        return Response({
            'session': CashSessionSerializer(session).data,
            'totals': {
                'opening_balance': session.opening_balance,
                'cash_sales': session.total_cash_sales,
                'cash_in': session.total_cash_in,
                'cash_out': session.total_cash_out,
                'expected_balance': session.expected_balance,
                'closing_balance': session.closing_balance,
                'difference': session.difference,
                'sales_count': session.sales_count
            }
        })


class CashMovementViewSet(viewsets.ModelViewSet):
    queryset = CashMovement.objects.all()
    serializer_class = CashMovementSerializer
    filterset_fields = ['cash_session', 'type']
    ordering_fields = ['created_at']
    
    def perform_create(self, serializer):
        # Validate session is open
        cash_session = serializer.validated_data['cash_session']
        
        if cash_session.status != SessionStatus.OPEN:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({'cash_session': 'Cannot add movements to closed sessions'})
        
        serializer.save(created_by=self.request.user)


from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.contrib.auth import get_user_model

from .models import Device, CashRegister, PriceChecker, StockTerminal
from .serializers import (
    PolymorphicDeviceSerializer, DeviceListSerializer,
    CashRegisterSerializer, PriceCheckerSerializer, StockTerminalSerializer,
    DeviceAssignSerializer, DeviceHeartbeatSerializer
)

class DeviceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing all devices (polymorphic)
    
    Automatically returns the correct serializer based on device type
    """
    queryset = Device.objects.all()
    serializer_class = PolymorphicDeviceSerializer
    filterset_fields = ['is_active', 'is_online', 'assigned_user']
    search_fields = ['code', 'name', 'location', 'serial_number']
    ordering_fields = ['name', 'code', 'created_at', 'last_seen']

    def get_serializer_class(self):
        if self.action == 'list':
            return DeviceListSerializer
        return PolymorphicDeviceSerializer
    
    @action(detail=True, methods=['post'])
    def heartbeat(self, request, pk=None):
        """Device check-in endpoint"""
        device = self.get_object()
        device.heartbeat()
        
        return Response({
            'timestamp': device.last_seen,
            'message': f'Heartbeat received from {device.name}'
        })
    
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """Assign device to a user"""
        device = self.get_object()
        serializer = DeviceAssignSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        User = get_user_model()
        user = get_object_or_404(User, id=serializer.validated_data['user_id'])
        
        device.assign_to_user(user)
        
        return Response(
            PolymorphicDeviceSerializer(device).data,
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def unassign(self, request, pk=None):
        """Remove user assignment from device"""
        device = self.get_object()
        device.unassign_user()
        
        return Response(
            PolymorphicDeviceSerializer(device).data,
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'])
    def cash_registers(self, request):
        """Get all cash registers"""
        cash_registers = CashRegister.objects.filter(is_active=True)
        serializer = CashRegisterSerializer(cash_registers, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def price_checkers(self, request):
        """Get all price checkers"""
        price_checkers = PriceChecker.objects.filter(is_active=True)
        serializer = PriceCheckerSerializer(price_checkers, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stock_terminals(self, request):
        """Get all stock terminals"""
        stock_terminals = StockTerminal.objects.filter(is_active=True)
        serializer = StockTerminalSerializer(stock_terminals, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def online(self, request):
        """Get all online devices"""
        devices = Device.objects.filter(is_online=True, is_active=True)
        serializer = DeviceListSerializer(devices, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def offline(self, request):
        """Get all offline devices"""
        devices = Device.objects.filter(is_online=False, is_active=True)
        serializer = DeviceListSerializer(devices, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get summary statistics of all devices"""
        total = Device.objects.count()
        active = Device.objects.filter(is_active=True).count()
        online = Device.objects.filter(is_online=True).count()
        
        cash_registers = CashRegister.objects.count()
        price_checkers = PriceChecker.objects.count()
        stock_terminals = StockTerminal.objects.count()
        
        return Response({
            'total': total,
            'active': active,
            'online': online,
            'offline': active - online,
            'by_type': {
                'cash_registers': cash_registers,
                'price_checkers': price_checkers,
                'stock_terminals': stock_terminals,
            }
        })

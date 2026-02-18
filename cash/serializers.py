from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from decimal import Decimal

from .models import CashSession, CashMovement
from devices.models import CashRegister
from devices.serializers import CashRegisterSerializer
from users.serializers import UserSerializer


# CashRegisterSerializer is now in devices/serializers.py


class CashSessionListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing sessions"""
    cash_register_name = serializers.CharField(source='cash_register.name', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = CashSession
        fields = [
            'id', 'cash_register', 'cash_register_name', 'user', 'user_name',
            'status', 'opening_date', 'closing_date',
            'opening_balance', 'closing_balance'
        ]


class CashSessionSerializer(serializers.ModelSerializer):
    """Complete serializer with calculated fields"""
    cash_register_data = CashRegisterSerializer(source='cash_register', read_only=True)
    user_data = UserSerializer(source='user', read_only=True)
    
    total_cash_sales = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    total_cash_in = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    total_cash_out = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    expected_balance = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    difference = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    sales_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = CashSession
        fields = [
            'id', 'cash_register', 'cash_register_data', 'user', 'user_data',
            'status', 'opening_date', 'closing_date',
            'opening_balance', 'closing_balance',
            'total_cash_sales', 'total_cash_in', 'total_cash_out',
            'expected_balance', 'difference', 'sales_count',
            'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'opening_date', 'closing_date', 'status', 'created_at', 'updated_at']


class CashMovementSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    
    class Meta:
        model = CashMovement
        fields = [
            'id', 'cash_session', 'type', 'type_display',
            'amount', 'reason', 'description',
            'created_by', 'created_by_name', 'created_at'
        ]
        read_only_fields = ['created_by', 'created_at']


class OpenCashSessionSerializer(serializers.Serializer):
    """Serializer for opening a cash session"""
    cash_register = serializers.IntegerField()
    opening_balance = serializers.DecimalField(max_digits=12, decimal_places=2)
    
    def validate_opening_balance(self, value):
        if value < 0:
            raise serializers.ValidationError(_('Opening balance cannot be negative.'))
        return value


class CloseCashSessionSerializer(serializers.Serializer):
    """Serializer for closing a cash session"""
    closing_balance = serializers.DecimalField(max_digits=12, decimal_places=2)
    notes = serializers.CharField(required=False, allow_blank=True)
    
    def validate_closing_balance(self, value):
        if value < 0:
            raise serializers.ValidationError(_('Closing balance cannot be negative.'))
        return value

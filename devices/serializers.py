from rest_framework import serializers
from rest_polymorphic.serializers import PolymorphicSerializer
from django.utils.translation import gettext_lazy as _

from .models import Device, CashRegister, PriceChecker, StockTerminal, DeviceConfig
from users.serializers import UserSerializer


class DeviceConfigSerializer(serializers.ModelSerializer):
    """Serializer for device configuration key-value pairs"""
    class Meta:
        model = DeviceConfig
        fields = ['id', 'key', 'value', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class DeviceSerializer(serializers.ModelSerializer):
    """Base device serializer with all common fields"""
    assigned_user_data = UserSerializer(source='assigned_user', read_only=True)
    configurations = DeviceConfigSerializer(many=True, read_only=True)
    
    class Meta:
        model = Device
        fields = [
            'id', 'code', 'name', 'location',
            'model', 'serial_number',
            'ip_address', 'mac_address',
            'is_active', 'is_online', 'last_seen',
            'assigned_user', 'assigned_user_data', 'assigned_date',
            'configurations', 'notes',
            'created_at', 'updated_at',
            'polymorphic_ctype'  # Identifies type
        ]
        read_only_fields = ['is_online', 'last_seen', 'assigned_date', 'created_at', 'updated_at', 'polymorphic_ctype']


class CashRegisterSerializer(DeviceSerializer):
    """Cash register serializer with session info"""
    current_session_id = serializers.SerializerMethodField()
    has_open_session = serializers.SerializerMethodField()
    
    class Meta(DeviceSerializer.Meta):
        model = CashRegister
        fields = DeviceSerializer.Meta.fields + ['current_session_id', 'has_open_session']
    
    def get_current_session_id(self, obj):
        session = obj.current_session
        return session.id if session else None
    
    def get_has_open_session(self, obj):
        return obj.has_open_session


class PriceCheckerSerializer(DeviceSerializer):
    """Price checker terminal serializer"""
    class Meta(DeviceSerializer.Meta):
        model = PriceChecker
        fields = DeviceSerializer.Meta.fields + ['display_promotions', 'timeout_seconds']


class StockTerminalSerializer(DeviceSerializer):
    """Stock terminal serializer"""
    class Meta(DeviceSerializer.Meta):
        model = StockTerminal
        fields = DeviceSerializer.Meta.fields + ['can_receive_shipments', 'require_photo']


class PolymorphicDeviceSerializer(PolymorphicSerializer):
    """Polymorphic serializer that returns the correct serializer based on device type"""
    model_serializer_mapping = {
        Device: DeviceSerializer,
        CashRegister: CashRegisterSerializer,
        PriceChecker: PriceCheckerSerializer,
        StockTerminal: StockTerminalSerializer,
    }


class DeviceListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing devices"""
    device_type = serializers.SerializerMethodField()
    assigned_user_name = serializers.CharField(source='assigned_user.get_full_name', read_only=True)
    
    class Meta:
        model = Device
        fields = [
            'id', 'code', 'name', 'device_type', 'location',
            'is_active', 'is_online', 'assigned_user_name', 'last_seen'
        ]
    
    def get_device_type(self, obj):
        return obj.__class__.__name__


class DeviceAssignSerializer(serializers.Serializer):
    """Serializer for assigning device to user"""
    user_id = serializers.IntegerField(required=True)
    
    def validate_user_id(self, value):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError(_('User does not exist'))
        return value


class DeviceHeartbeatSerializer(serializers.Serializer):
    """Serializer for device heartbeat/check-in"""
    timestamp = serializers.DateTimeField(read_only=True)
    message = serializers.CharField(read_only=True)


class DeviceConfigUpdateSerializer(serializers.Serializer):
    """Serializer for updating device configuration"""
    key = serializers.CharField(max_length=100)
    value = serializers.CharField(max_length=500)

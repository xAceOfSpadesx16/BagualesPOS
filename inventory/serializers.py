from rest_framework import serializers
from .models import Inventory, StockAdjustmentRequest, StockMovement, StockTransfer, StockTransferDetail
from products.serializers import ProductListSerializer

class InventorySerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    
    class Meta:
        model = Inventory
        fields = ['id', 'product', 'branch', 'quantity']


class StockAdjustmentRequestSerializer(serializers.ModelSerializer):
    """Serializer for Stock Adjustment Requests"""
    product_data = ProductListSerializer(source='product', read_only=True)
    requested_by_name = serializers.CharField(source='requested_by.get_full_name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    
    class Meta:
        model = StockAdjustmentRequest
        fields = [
            'id', 'company', 'branch', 'branch_name', 'product', 'product_data',
            'adjustment_type', 'quantity', 'reason', 'status',
            'requested_by', 'requested_by_name', 'approved_by', 'approved_by_name',
            'rejection_note', 'created_at', 'updated_at'
        ]
        read_only_fields = ['company', 'branch', 'status', 'requested_by', 'approved_by', 'created_at', 'updated_at']


class StockMovementSerializer(serializers.ModelSerializer):
    """Serializer for Stock Movements (read-only audit log)"""
    product_data = ProductListSerializer(source='product', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    
    class Meta:
        model = StockMovement
        fields = [
            'id', 'company', 'branch', 'branch_name', 'product', 'product_data',
            'movement_type', 'previous_quantity', 'new_quantity', 'quantity_change',
            'reference_id', 'reference_model', 'notes',
            'created_by', 'created_by_name', 'created_at'
        ]
        read_only_fields = [
            'company', 'branch', 'product', 'movement_type',
            'previous_quantity', 'new_quantity', 'quantity_change',
            'reference_id', 'reference_model', 'notes', 'created_by'
        ]


# Stock Transfer Serializers

class StockTransferDetailItemSerializer(serializers.ModelSerializer):
    product_data = ProductListSerializer(source='product', read_only=True)

    class Meta:
        model = StockTransferDetail
        fields = [
            'id', 'transfer', 'product', 'product_data', 'quantity',
            'origin_stock_before', 'origin_stock_after',
        ]


class StockTransferListSerializer(serializers.ModelSerializer):
    origin_branch_name = serializers.CharField(source='origin_branch.name', read_only=True)
    destination_branch_name = serializers.CharField(source='destination_branch.name', read_only=True)
    requested_by_name = serializers.CharField(source='requested_by.get_full_name', read_only=True)
    approved_by_name = serializers.SerializerMethodField()
    total_items = serializers.ReadOnlyField()
    total_units = serializers.ReadOnlyField()
    details = StockTransferDetailItemSerializer(many=True, read_only=True)

    class Meta:
        model = StockTransfer
        fields = [
            'id', 'company', 'origin_branch', 'origin_branch_name',
            'destination_branch', 'destination_branch_name',
            'status', 'requested_by', 'requested_by_name',
            'approved_by', 'approved_by_name', 'rejection_note',
            'notes', 'total_items', 'total_units',
            'created_at', 'updated_at', 'details',
        ]
        read_only_fields = ['company', 'status', 'requested_by', 'approved_by', 'created_at', 'updated_at']

    def get_approved_by_name(self, obj) -> str:
        return obj.approved_by.get_full_name() if obj.approved_by else ''


class StockTransferCreateSerializer(serializers.ModelSerializer):
    """Serializer de escritura para crear transferencias."""
    details = StockTransferDetailItemSerializer(many=True)

    class Meta:
        model = StockTransfer
        fields = ['origin_branch', 'destination_branch', 'notes', 'details']

    def validate(self, data):
        if data['origin_branch'] == data['destination_branch']:
            raise serializers.ValidationError({
                'destination_branch': 'Origin and destination branches must be different.'
            })
        if not data.get('details'):
            raise serializers.ValidationError({'details': 'At least one detail is required.'})
        return data

    def create(self, validated_data):
        details_data = validated_data.pop('details')
        transfer = StockTransfer.objects.create(**validated_data)
        for detail_data in details_data:
            StockTransferDetail.objects.create(transfer=transfer, **detail_data)
        return transfer

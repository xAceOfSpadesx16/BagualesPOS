from rest_framework import serializers
from .models import Inventory, StockAdjustmentRequest, StockMovement
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

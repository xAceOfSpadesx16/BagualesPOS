from rest_framework import serializers
from .models import Inventory
from products.serializers import ProductListSerializer

class InventorySerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    
    class Meta:
        model = Inventory
        fields = ['id', 'product', 'branch', 'quantity']

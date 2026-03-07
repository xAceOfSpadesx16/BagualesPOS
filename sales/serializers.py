from rest_framework import serializers
from .models import Sale, SaleDetail, PayMethod
from products.serializers import ProductListSerializer
from clients.serializers import ClientSerializer

class PayMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayMethod
        fields = '__all__'

class SaleDetailSerializer(serializers.ModelSerializer):
    product_data = ProductListSerializer(source='product', read_only=True)
    formatted_total_price = serializers.ReadOnlyField()
    formatted_sale_price = serializers.ReadOnlyField()
    formatted_cost_price = serializers.ReadOnlyField()
    profit = serializers.ReadOnlyField()
    profit_margin = serializers.ReadOnlyField()

    class Meta:
        model = SaleDetail
        fields = [
            'id', 'order', 'product', 'product_data', 'quantity', 
            'sale_price', 'cost_price', 'formatted_sale_price', 'formatted_cost_price',
            'formatted_total_price', 'profit', 'profit_margin',
            'created_at'
        ]
        read_only_fields = ['sale_price', 'cost_price']

class SaleSerializer(serializers.ModelSerializer):
    details = SaleDetailSerializer(many=True, read_only=True)
    client_data = ClientSerializer(source='client', read_only=True)
    formatted_total_amount = serializers.ReadOnlyField()
    seller_name = serializers.CharField(source='seller.get_full_name', read_only=True)
    is_credit_sale = serializers.ReadOnlyField()
    cash_session_data = serializers.SerializerMethodField()
    branch_name = serializers.CharField(source='branch.name', read_only=True)

    class Meta:
        model = Sale
        fields = [
            'id', 'seller', 'seller_name', 'client', 'client_data', 
            'total_amount', 'formatted_total_amount', 'pay_method', 
            'payment_status', 'is_credit_sale', 'account_record_id',
            'cash_session', 'cash_session_data', 'branch', 'branch_name',
            'canceled', 'closed', 'created_at', 'updated_at', 'details'
        ]
        read_only_fields = ['total_amount', 'seller', 'account_record_id', 'payment_status', 'cash_session', 'branch']
    
    def get_cash_session_data(self, obj):
        """Return basic cash session info"""
        if obj.cash_session:
            return {
                'id': obj.cash_session.id,
                'cash_register': obj.cash_session.cash_register.name if obj.cash_session.cash_register else None,
                'opening_date': obj.cash_session.opening_date,
                'status': obj.cash_session.status
            }
        return None


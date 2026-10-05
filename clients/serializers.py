from rest_framework import serializers
from .models import Client, CustomerAccount, CustomerBalanceRecord

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'deleted_at']

    total_purchases = serializers.SerializerMethodField()
    last_purchase = serializers.SerializerMethodField()

    def get_total_purchases(self, obj):
        """Calculate total purchases for the client"""
        # Using sale _set because Sale model doesn't have related_name='sales'
        return obj.sale_set.filter(canceled=False, closed=True).count()

    def get_last_purchase(self, obj):
        """Get the date of the last purchase"""
        last_sale = obj.sale_set.filter(canceled=False, closed=True).order_by('-created_at').first()
        return last_sale.created_at if last_sale else None


    customer_account = serializers.SerializerMethodField()

    def get_customer_account(self, obj):
        """Return customer account data without circular reference"""
        if hasattr(obj, 'customer_account'):
            account = obj.customer_account
            return {
                'id': account.id,
                'credit_limit': account.credit_limit,
                'active': account.active,
                'balance': account.balance,
                'opening_date': account.opening_date
            }
        return None


class CustomerAccountSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.name', read_only=True)
    client_dni = serializers.CharField(source='client.dni', read_only=True)
    client_id = serializers.PrimaryKeyRelatedField(
        queryset=Client.objects.all(), source='client', write_only=True
    )
    balance = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = CustomerAccount
        fields = [
            'id', 'client', 'client_id', 'client_name', 'client_dni',
            'credit_limit', 'active', 'notes', 'opening_date', 'balance'
        ]
        read_only_fields = ['opening_date', 'client']


class CustomerBalanceRecordSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)
    reconciled_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = CustomerBalanceRecord
        fields = '__all__'
        read_only_fields = ['created_at', 'created_by', 'reconciled_at', 'reconciled_by']

    def validate(self, data):
        instance = CustomerBalanceRecord(**data)
        # We need to set the customer_account if it's not in data (e.g. partial update)
        # But for create it should be there.
        # For update, we should merge with existing instance.
        if self.instance:
            instance = self.instance
            for key, value in data.items():
                setattr(instance, key, value)
        
        try:
            instance.clean()
        except Exception as e:
            raise serializers.ValidationError(e.message_dict if hasattr(e, 'message_dict') else str(e))
        return data

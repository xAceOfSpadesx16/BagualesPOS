from rest_framework import serializers
from .models import Sale, SaleDetail, PayMethod, Return, ReturnDetail, ReturnRefund
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


# Return Serializers

class ReturnDetailItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = ReturnDetail
        fields = [
            'id', 'return_obj', 'sale_detail', 'product', 'product_name',
            'quantity', 'unit_price', 'subtotal', 'condition', 'restock',
        ]


class ReturnRefundItemSerializer(serializers.ModelSerializer):
    pay_method_name = serializers.CharField(source='pay_method.name', read_only=True, default='')

    class Meta:
        model = ReturnRefund
        fields = [
            'id', 'return_obj', 'refund_method', 'pay_method',
            'pay_method_name', 'amount', 'account_record',
        ]


class ReturnListSerializer(serializers.ModelSerializer):
    sale_client_name = serializers.SerializerMethodField()
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    reason_display = serializers.CharField(source='get_reason_type_display', read_only=True)
    processed_by_name = serializers.CharField(source='processed_by.get_full_name', read_only=True, default='')
    authorized_by_name = serializers.CharField(source='authorized_by.get_full_name', read_only=True, default='')

    class Meta:
        model = Return
        fields = [
            'id', 'sale', 'sale_client_name', 'branch', 'branch_name',
            'cash_session', 'status', 'reason_display', 'reason_type',
            'reason_notes', 'total_refund_amount', 'processed_by',
            'processed_by_name', 'authorized_by', 'authorized_by_name',
            'created_at', 'updated_at',
        ]

    def get_sale_client_name(self, obj) -> str:
        client = obj.sale.client
        return f'{client.name} {client.last_name}' if client else ''


class ReturnDetailResponseSerializer(ReturnListSerializer):
    details = ReturnDetailItemSerializer(many=True, read_only=True)
    refunds = ReturnRefundItemSerializer(many=True, read_only=True)

    class Meta(ReturnListSerializer.Meta):
        fields = ReturnListSerializer.Meta.fields + ['details', 'refunds']


class ReturnCreateSerializer(serializers.ModelSerializer):
    """Serializer de escritura para crear devoluciones."""
    details = ReturnDetailItemSerializer(many=True)
    refunds = ReturnRefundItemSerializer(many=True)

    class Meta:
        model = Return
        fields = ['sale', 'reason_type', 'reason_notes', 'details', 'refunds']

    def validate(self, data):
        sale = data['sale']
        if not sale.closed:
            raise serializers.ValidationError({'sale': 'Sale must be closed to process a return.'})
        if sale.canceled:
            raise serializers.ValidationError({'sale': 'Cannot return items from a canceled sale.'})

        details = data.get('details', [])
        refunds = data.get('refunds', [])

        if not details:
            raise serializers.ValidationError({'details': 'At least one detail is required.'})

        # Validar que la suma de refunds coincida con la de details
        total_detail = sum(d['subtotal'] for d in details)
        total_refund = sum(r['amount'] for r in refunds)
        if refunds and total_refund != total_detail:
            raise serializers.ValidationError({
                'refunds': f'Refund total ({total_refund}) must equal detail total ({total_detail}).'
            })

        return data

    def create(self, validated_data):
        details_data = validated_data.pop('details')
        refunds_data = validated_data.pop('refunds')

        ret = Return.objects.create(**validated_data)

        for detail_data in details_data:
            ReturnDetail.objects.create(return_obj=ret, **detail_data)

        for refund_data in refunds_data:
            ReturnRefund.objects.create(return_obj=ret, **refund_data)

        # Calcular total
        ret.total_refund_amount = sum(d.subtotal for d in ret.details.all())
        ret.save()

        return ret


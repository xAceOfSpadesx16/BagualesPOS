from django.db.models import Model
from django.db.models.fields import DateTimeField, BooleanField, CharField, IntegerField, DecimalField, TextField, PositiveIntegerField
from django.db.models.fields.related import ForeignKey
from django.db.models.deletion import CASCADE, SET_NULL
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django_multitenant.models import TenantModel

from sales.managers import SalesManager
from sales.choices import PaymentStatus, ReturnStatus, ReturnReasonType, ReturnCondition, RefundMethod
from products.models import Product
from clients.models import Client, CustomerBalanceRecord

from utils.formats import formatted_integer
from decimal import Decimal

class PayMethod(TenantModel):
    tenant_id = 'company_id'
    
    company = ForeignKey('core.Company', on_delete=CASCADE, related_name='payment_methods', verbose_name=_('company'), null=True, blank=True)
    name = CharField(max_length=50, verbose_name= _('name'))
    created_at = DateTimeField(auto_now_add=True, editable= False, verbose_name= _('created at'))
    updated_at = DateTimeField(auto_now=True, verbose_name= _('updated at'))

    class Meta:
        verbose_name = _('payment method')
        verbose_name_plural = _('payment methods')
        unique_together = [['company', 'name']]

    def __str__(self):
        return self.name

class Sale(TenantModel):
    tenant_id = 'company_id'
    
    company = ForeignKey('core.Company', on_delete=CASCADE, related_name='sales', verbose_name=_('company'), null=True, blank=True)
    seller = ForeignKey(get_user_model(), on_delete=SET_NULL, null=True, verbose_name= _('seller'))
    client = ForeignKey(Client, on_delete=SET_NULL, null=True, blank=True, verbose_name= _('client'))
    total_amount = DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name= _('total amount'))
    pay_method = ForeignKey(PayMethod, on_delete=SET_NULL, null=True, verbose_name= _('payment method'))
    payment_status = CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING, verbose_name= _('payment status'))
    account_record = ForeignKey(CustomerBalanceRecord, on_delete=SET_NULL, null=True, blank=True, related_name='sales', verbose_name=_('account record'))
    cash_session = ForeignKey('cash.CashSession', on_delete=SET_NULL, null=True, blank=True, related_name='sales', verbose_name=_('cash session'))
    branch = ForeignKey('core.Branch', on_delete=SET_NULL, null=True, blank=True, related_name='sales', verbose_name=_('branch'), help_text=_('Branch where this sale was made'))
    canceled = BooleanField(default=False, verbose_name= _('canceled'))
    closed = BooleanField(default=False, verbose_name= _('closed'))
    created_at = DateTimeField(auto_now_add=True, verbose_name= _('created at'))
    updated_at = DateTimeField(auto_now=True, verbose_name= _('updated at'))

    objects: SalesManager = SalesManager()

    class Meta:
        verbose_name = _('sale')
        verbose_name_plural = _('sales')
        ordering = ['-created_at']

    def __str__(self):
        return f'{_('sale')} {self.pk} - {self.seller.get_full_name()} - {self.created_at} {f"- {self.client.name}" if self.client else ""}'
    
    @property
    def formatted_total_amount(self):
        return formatted_integer(int(self.total_amount))
    
    @property
    def is_credit_sale(self):
        """Returns True if this is a credit sale (cliente con cuenta corriente)"""
        return self.client and hasattr(self.client, 'customer_account') and self.client.customer_account.active
    
    def clean(self):
        """Validate sale before saving"""
        super().clean()

        
        # New validation: cash_session required for closed sales
        if self.closed and not self.cash_session:
            raise ValidationError({
                'cash_session': _('Cash session is required for closed sales.')
            })
        
        # New validation: pay_method required for closed sales
        if self.closed and not self.pay_method:
            raise ValidationError({
                'pay_method': _('Payment method is required for closed sales.')
            })
    
    def save(self, *args, **kwargs):
        """Auto-populate branch from cash_session if available"""
        # Auto-populate branch from cash_session.cash_register.branch
        if self.cash_session and not self.branch:
            if hasattr(self.cash_session.cash_register, 'branch'):
                self.branch = self.cash_session.cash_register.branch
        
        super().save(*args, **kwargs)

    

class SaleDetail(TenantModel):
    tenant_id = 'company_id'
    
    company = ForeignKey('core.Company', on_delete=CASCADE, related_name='sale_details', verbose_name=_('company'), null=True, blank=True)
    order = ForeignKey(Sale, on_delete=CASCADE, related_name='details', verbose_name= _('order'))
    product = ForeignKey(Product, on_delete= SET_NULL, null=True, verbose_name= _('product'))
    quantity = IntegerField(default=1, help_text='Cantidad', verbose_name= _('quantity'))
    sale_price = DecimalField(max_digits=10, decimal_places=2, verbose_name= _('sale price'))
    cost_price = DecimalField(max_digits=10, decimal_places=2, verbose_name= _('cost price'))
    created_at = DateTimeField(auto_now_add=True, verbose_name= _('created at'))

    class Meta:
        verbose_name = _('sale detail')
        verbose_name_plural = _('sale details')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.product} - {self.quantity} - {self.sale_price}'
    
    @property
    def get_total_price(self):
        return self.quantity * self.sale_price
    
    @property
    def get_total_cost(self):
        return self.quantity * self.cost_price
    
    @property
    def profit(self):
        """Calculate profit for this sale detail"""
        return self.get_total_price - self.get_total_cost
    
    @property
    def profit_margin(self):
        """Calculate profit margin as percentage"""
        if self.get_total_price > 0:
            return Decimal(str((self.profit / self.get_total_price) * 100))
        return Decimal('0.00')
    
    @property
    def formatted_total_price(self):
        return formatted_integer(int(self.get_total_price))
    
    @property
    def formatted_sale_price(self):
        return formatted_integer(int(self.sale_price))
    
    @property
    def formatted_cost_price(self):
        return formatted_integer(int(self.cost_price))
    
    def clean(self):
        """Validate before saving"""
        super().clean()
        
        # Validate product exists
        if not self.product:
            raise ValidationError({'product': _('Product is required.')})
        
        # Validate positive quantity
        if self.quantity <= 0:
            raise ValidationError({'quantity': _('Quantity must be greater than zero.')})
        
        # Prevent adding items to closed or canceled sales
        if self.order_id and self.order.closed:
            raise ValidationError({'order': _('Cannot add or modify items in a closed sale.')})
        if self.order_id and self.order.canceled:
            raise ValidationError({'order': _('Cannot add or modify items in a canceled sale.')})
        
        # Validate stock availability (only for new or increased quantity)
        if self.product and getattr(self, 'order', None) and self.order.branch:
            from inventory.models import Inventory
            try:
                inventory = Inventory.objects.get(product=self.product, branch=self.order.branch)
                old_quantity = 0
                if self.pk:
                    try:
                        old_instance = SaleDetail.objects.get(pk=self.pk)
                        old_quantity = old_instance.quantity
                    except SaleDetail.DoesNotExist:
                        pass
                
                quantity_diff = self.quantity - old_quantity
                if quantity_diff > 0:  # Only check if increasing quantity
                    available_stock = inventory.quantity
                    if available_stock < quantity_diff:
                        raise ValidationError({
                            'quantity': _(f'Insufficient stock. Available: {available_stock}, Requested: {quantity_diff}')
                        })
            except Inventory.DoesNotExist:
                raise ValidationError({
                    'product': _('This product has no inventory registered for the assigned branch.')
                })

    def save(self, *args, **kwargs):
        # Capture prices from product if not set
        if self.product:
            if self.sale_price is None:
                self.sale_price = self.product.sale_price
            if self.cost_price is None:
                self.cost_price = self.product.cost_price
        super().save(*args, **kwargs)


class Return(TenantModel):
    """Devolución asociada a una venta."""
    tenant_id = 'company_id'

    company = ForeignKey('core.Company', on_delete=CASCADE, related_name='returns', verbose_name=_('company'))
    sale = ForeignKey(Sale, on_delete=CASCADE, related_name='returns', verbose_name=_('sale'))
    branch = ForeignKey('core.Branch', on_delete=CASCADE, related_name='returns', verbose_name=_('branch'))
    cash_session = ForeignKey('cash.CashSession', on_delete=SET_NULL, null=True, blank=True, related_name='returns', verbose_name=_('cash session'))
    status = CharField(max_length=20, choices=ReturnStatus.choices, default=ReturnStatus.COMPLETED, verbose_name=_('status'))
    reason_type = CharField(max_length=20, choices=ReturnReasonType.choices, verbose_name=_('reason type'))
    reason_notes = TextField(blank=True, default='', verbose_name=_('reason notes'))
    total_refund_amount = DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name=_('total refund amount'))
    processed_by = ForeignKey(get_user_model(), on_delete=SET_NULL, null=True, related_name='returns_processed', verbose_name=_('processed by'))
    authorized_by = ForeignKey(get_user_model(), on_delete=SET_NULL, null=True, blank=True, related_name='returns_authorized', verbose_name=_('authorized by'))
    created_at = DateTimeField(auto_now_add=True, verbose_name=_('created at'))
    updated_at = DateTimeField(auto_now=True, verbose_name=_('updated at'))

    class Meta:
        verbose_name = _('return')
        verbose_name_plural = _('returns')
        ordering = ['-created_at']

    def __str__(self):
        return f'Return #{self.pk} - Sale #{self.sale_id}'


class ReturnDetail(TenantModel):
    """Línea de producto en una devolución."""
    tenant_id = 'company_id'

    company = ForeignKey('core.Company', on_delete=CASCADE, related_name='return_details', verbose_name=_('company'))
    return_obj = ForeignKey(Return, on_delete=CASCADE, related_name='details', verbose_name=_('return'))
    sale_detail = ForeignKey(SaleDetail, on_delete=CASCADE, verbose_name=_('sale detail'))
    product = ForeignKey(Product, on_delete=CASCADE, verbose_name=_('product'))
    quantity = PositiveIntegerField(verbose_name=_('quantity'))
    unit_price = DecimalField(max_digits=12, decimal_places=2, verbose_name=_('unit price'))
    subtotal = DecimalField(max_digits=12, decimal_places=2, verbose_name=_('subtotal'))
    condition = CharField(max_length=20, choices=ReturnCondition.choices, default=ReturnCondition.RESALEABLE, verbose_name=_('condition'))
    restock = BooleanField(default=True, verbose_name=_('restock'))

    class Meta:
        verbose_name = _('return detail')
        verbose_name_plural = _('return details')

    def __str__(self):
        return f'{self.product} x{self.quantity}'


class ReturnRefund(TenantModel):
    """Registro de reembolso asociado a una devolución."""
    tenant_id = 'company_id'

    company = ForeignKey('core.Company', on_delete=CASCADE, related_name='return_refunds', verbose_name=_('company'))
    return_obj = ForeignKey(Return, on_delete=CASCADE, related_name='refunds', verbose_name=_('return'))
    refund_method = CharField(max_length=20, choices=RefundMethod.choices, verbose_name=_('refund method'))
    pay_method = ForeignKey(PayMethod, on_delete=SET_NULL, null=True, blank=True, verbose_name=_('pay method'))
    amount = DecimalField(max_digits=12, decimal_places=2, verbose_name=_('amount'))
    account_record = ForeignKey(CustomerBalanceRecord, on_delete=SET_NULL, null=True, blank=True, verbose_name=_('account record'))

    class Meta:
        verbose_name = _('return refund')
        verbose_name_plural = _('return refunds')

    def __str__(self):
        return f'Refund {self.refund_method} - {self.amount}'


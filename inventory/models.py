from django.db import models
from django.db.models import Model, CASCADE, SET_NULL, Sum, TextChoices
from django.db.models.fields import IntegerField, CharField, DateTimeField, TextField, PositiveIntegerField
from django.db.models.fields.related import OneToOneField, ForeignKey
from django.utils.translation import gettext_lazy as _
from django_multitenant.models import TenantModel
from django.contrib.auth import get_user_model

from inventory.managers import InventoryManager

from products.models import Product

User = get_user_model()

class Inventory(TenantModel):
    tenant_id = 'company_id'
    
    company = ForeignKey('core.Company', on_delete=CASCADE, related_name='inventories', verbose_name=_('company'), null=True, blank=True)
    branch = ForeignKey('core.Branch', on_delete=CASCADE, related_name='inventories', verbose_name=_('branch'), null=True, blank=True)
    product = ForeignKey(Product, on_delete=CASCADE, related_name='inventories', verbose_name=_('product'))
    quantity = IntegerField(default=0, verbose_name=_('quantity'))

    objects: InventoryManager = InventoryManager()

    def __str__(self):
        return f'{self.product} - {self.quantity}'
    
    def update_quantity(self, quantity: int) -> None:
        """ Quantity += new quantity """
        self.quantity += quantity
        self.save()
        
    class Meta:
        verbose_name = _('inventory')
        verbose_name_plural = _('inventories')
        unique_together = [['product', 'branch']]


class StockAdjustmentRequest(TenantModel):
    """
    Model for stock adjustment requests.
    Branch managers request adjustments, which must be approved by General Admins.
    """
    tenant_id = 'company_id'
    
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        APPROVED = 'APPROVED', _('Approved')
        REJECTED = 'REJECTED', _('Rejected')
    
    class AdjustmentType(models.TextChoices):
        REDUCTION = 'REDUCTION', _('Stock Reduction')
        ADDITION = 'ADDITION', _('Stock Addition')
        CORRECTION = 'CORRECTION', _('Stock Correction')
    
    company = ForeignKey('core.Company', on_delete=CASCADE, related_name='stock_adjustment_requests', verbose_name=_('company'))
    branch = ForeignKey('core.Branch', on_delete=CASCADE, related_name='stock_adjustment_requests', verbose_name=_('branch'))
    product = ForeignKey(Product, on_delete=CASCADE, related_name='stock_adjustment_requests', verbose_name=_('product'))
    adjustment_type = CharField(max_length=20, choices=AdjustmentType.choices, default=AdjustmentType.REDUCTION, verbose_name=_('adjustment type'))
    quantity = IntegerField(verbose_name=_('quantity'), help_text=_('Quantity to adjust (positive or negative)'))
    reason = TextField(verbose_name=_('reason'), help_text=_('Reason for the adjustment'))
    status = CharField(max_length=20, choices=Status.choices, default=Status.PENDING, verbose_name=_('status'))
    requested_by = ForeignKey(User, on_delete=SET_NULL, null=True, related_name='stock_adjustments_requested', verbose_name=_('requested by'))
    approved_by = ForeignKey(User, on_delete=SET_NULL, null=True, blank=True, related_name='stock_adjustments_approved', verbose_name=_('approved by'))
    rejection_note = TextField(blank=True, null=True, verbose_name=_('rejection note'))
    created_at = DateTimeField(auto_now_add=True, verbose_name=_('created at'))
    updated_at = DateTimeField(auto_now=True, verbose_name=_('updated at'))
    
    class Meta:
        verbose_name = _('stock adjustment request')
        verbose_name_plural = _('stock adjustment requests')
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.adjustment_type} - {self.product} - {self.quantity} ({self.status})'


class StockMovement(TenantModel):
    """
    Immutable audit log for all stock movements.
    Records every change to inventory quantities.
    """
    tenant_id = 'company_id'
    
    class MovementType(models.TextChoices):
        SALE = 'SALE', _('Sale')
        ADJUSTMENT = 'ADJUSTMENT', _('Manual Adjustment')
        RETURN = 'RETURN', _('Return')
        TRANSFER = 'TRANSFER', _('Transfer')
        CORRECTION = 'CORRECTION', _('Correction')
    
    company = ForeignKey('core.Company', on_delete=CASCADE, related_name='stock_movements', verbose_name=_('company'))
    branch = ForeignKey('core.Branch', on_delete=CASCADE, related_name='stock_movements', verbose_name=_('branch'))
    product = ForeignKey(Product, on_delete=CASCADE, related_name='stock_movements', verbose_name=_('product'))
    movement_type = CharField(max_length=20, choices=MovementType.choices, verbose_name=_('movement type'))
    previous_quantity = IntegerField(verbose_name=_('previous quantity'))
    new_quantity = IntegerField(verbose_name=_('new quantity'))
    quantity_change = IntegerField(verbose_name=_('quantity change'))
    reference_id = IntegerField(null=True, blank=True, verbose_name=_('reference ID'), help_text=_('ID of related record (sale, adjustment, etc.)'))
    reference_model = CharField(max_length=50, null=True, blank=True, verbose_name=_('reference model'))
    notes = TextField(blank=True, null=True, verbose_name=_('notes'))
    created_by = ForeignKey(User, on_delete=SET_NULL, null=True, related_name='stock_movements_created', verbose_name=_('created by'))
    created_at = DateTimeField(auto_now_add=True, verbose_name=_('created at'))
    
    class Meta:
        verbose_name = _('stock movement')
        verbose_name_plural = _('stock movements')
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.movement_type} - {self.product} - {self.quantity_change} ({self.created_at})'


class StockTransfer(TenantModel):
    """Transferencia de stock entre sucursales."""
    tenant_id = 'company_id'

    class Status(TextChoices):
        PENDING = 'PENDING', _('Pending')
        IN_TRANSIT = 'IN_TRANSIT', _('In Transit')
        COMPLETED = 'COMPLETED', _('Completed')
        REJECTED = 'REJECTED', _('Rejected')

    company = ForeignKey('core.Company', on_delete=CASCADE, related_name='stock_transfers', verbose_name=_('company'))
    origin_branch = ForeignKey('core.Branch', on_delete=CASCADE, related_name='outgoing_transfers', verbose_name=_('origin branch'))
    destination_branch = ForeignKey('core.Branch', on_delete=CASCADE, related_name='incoming_transfers', verbose_name=_('destination branch'))
    status = CharField(max_length=20, choices=Status.choices, default=Status.PENDING, verbose_name=_('status'))
    requested_by = ForeignKey(User, on_delete=SET_NULL, null=True, related_name='transfers_requested', verbose_name=_('requested by'))
    approved_by = ForeignKey(User, on_delete=SET_NULL, null=True, blank=True, related_name='transfers_approved', verbose_name=_('approved by'))
    rejection_note = TextField(blank=True, default='', verbose_name=_('rejection note'))
    notes = TextField(blank=True, default='', verbose_name=_('notes'))
    created_at = DateTimeField(auto_now_add=True, verbose_name=_('created at'))
    updated_at = DateTimeField(auto_now=True, verbose_name=_('updated at'))

    class Meta:
        verbose_name = _('stock transfer')
        verbose_name_plural = _('stock transfers')
        ordering = ['-created_at']

    def __str__(self):
        return f'Transfer #{self.pk} - {self.origin_branch} → {self.destination_branch} ({self.status})'

    @property
    def total_items(self) -> int:
        return self.details.count()

    @property
    def total_units(self) -> int:
        return self.details.aggregate(total=Sum('quantity'))['total'] or 0


class StockTransferDetail(TenantModel):
    """Línea de producto en una transferencia de stock."""
    tenant_id = 'company_id'

    transfer = ForeignKey(StockTransfer, on_delete=CASCADE, related_name='details', verbose_name=_('transfer'))
    product = ForeignKey(Product, on_delete=CASCADE, verbose_name=_('product'))
    quantity = PositiveIntegerField(verbose_name=_('quantity'))
    origin_stock_before = IntegerField(null=True, blank=True, verbose_name=_('origin stock before'))
    origin_stock_after = IntegerField(null=True, blank=True, verbose_name=_('origin stock after'))

    class Meta:
        verbose_name = _('stock transfer detail')
        verbose_name_plural = _('stock transfer details')

    def __str__(self):
        return f'{self.product} x{self.quantity}'

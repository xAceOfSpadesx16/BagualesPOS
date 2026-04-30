from django.db import models
from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _
from django_multitenant.models import TenantModel
from django.contrib.auth import get_user_model

User = get_user_model()


class AuditRecord(TenantModel):
    """Registro inmutable de auditoría para todas las acciones del sistema."""
    tenant_id = 'company_id'

    class Action(TextChoices):
        SALE_CREATED = 'SALE_CREATED', _('Sale Created')
        SALE_CANCELED = 'SALE_CANCELED', _('Sale Canceled')
        ADJUSTMENT_CREATED = 'ADJUSTMENT_CREATED', _('Adjustment Created')
        ADJUSTMENT_APPROVED = 'ADJUSTMENT_APPROVED', _('Adjustment Approved')
        ADJUSTMENT_REJECTED = 'ADJUSTMENT_REJECTED', _('Adjustment Rejected')
        RETURN_PROCESSED = 'RETURN_PROCESSED', _('Return Processed')
        RETURN_CANCELED = 'RETURN_CANCELED', _('Return Canceled')
        TRANSFER_CREATED = 'TRANSFER_CREATED', _('Transfer Created')
        TRANSFER_APPROVED = 'TRANSFER_APPROVED', _('Transfer Approved')
        TRANSFER_COMPLETED = 'TRANSFER_COMPLETED', _('Transfer Completed')
        PRICE_CHANGED = 'PRICE_CHANGED', _('Price Changed')
        PRICE_BULK_UPDATE = 'PRICE_BULK_UPDATE', _('Bulk Price Update')
        CASH_SESSION_OPENED = 'CASH_SESSION_OPENED', _('Cash Session Opened')
        CASH_SESSION_CLOSED = 'CASH_SESSION_CLOSED', _('Cash Session Closed')
        INVENTORY_UPDATED = 'INVENTORY_UPDATED', _('Inventory Updated')
        SETTINGS_UPDATED = 'SETTINGS_UPDATED', _('Settings Updated')

    company = models.ForeignKey('core.Company', on_delete=models.CASCADE, related_name='audit_records', verbose_name=_('company'))
    branch = models.ForeignKey('core.Branch', on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_records', verbose_name=_('branch'))
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_records', verbose_name=_('user'))
    action = models.CharField(max_length=30, choices=Action.choices, verbose_name=_('action'))
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name=_('IP address'))
    description = models.TextField(blank=True, default='', verbose_name=_('description'))
    details = models.JSONField(default=dict, blank=True, verbose_name=_('details'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('created at'))

    class Meta:
        verbose_name = _('audit record')
        verbose_name_plural = _('audit records')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.action} - {self.user} - {self.created_at}'

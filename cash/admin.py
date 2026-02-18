from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from decimal import Decimal

from .models import CashSession, CashMovement
from .choices import SessionStatus


# CashRegister is now in devices app
# See devices/admin.py for CashRegister admin


@admin.register(CashSession)
class CashSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'cash_register', 'user', 'status', 'opening_date', 'closing_date', 'difference']
    list_filter = ['status', 'opening_date', 'closing_date']
    search_fields = ['cash_register__name', 'user__username']
    readonly_fields = ['opening_date', 'expected_balance', 'difference', 'total_cash_sales', 'total_cash_in', 'total_cash_out']
    date_hierarchy = 'opening_date'
    
    fieldsets = (
        (_('Session Info'), {
            'fields': ('cash_register', 'user', 'status')
        }),
        (_('Balances'), {
            'fields': ('opening_balance', 'closing_balance', 'expected_balance', 'difference')
        }),
        (_('Totals'), {
            'fields': ('total_cash_sales', 'total_cash_in', 'total_cash_out')
        }),
        (_('Dates'), {
            'fields': ('opening_date', 'closing_date')
        }),
        (_('Notes'), {
            'fields': ('notes',)
        }),
    )
    
    def difference(self, obj):
        diff = obj.difference
        if diff > 0:
            return f'+{diff}'
        return str(diff)
    difference.short_description = _('Difference')


@admin.register(CashMovement)
class CashMovementAdmin(admin.ModelAdmin):
    list_display = ['id', 'cash_session', 'type', 'amount', 'reason', 'created_by', 'created_at']
    list_filter = ['type', 'created_at']
    search_fields = ['cash_session__cash_register__name', 'reason', 'created_by__username']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (_('Movement Info'), {
            'fields': ('cash_session', 'type', 'amount', 'reason')
        }),
        (_('Metadata'), {
            'fields': ('created_by', 'created_at')
        }),
    )

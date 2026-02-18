from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin, PolymorphicChildModelFilter

from .models import Device, CashRegister, PriceChecker, StockTerminal, DeviceConfig


class DeviceConfigInline(admin.TabularInline):
    model = DeviceConfig
    extra = 1
    fields = ['key', 'value']


class DeviceChildAdmin(PolymorphicChildModelAdmin):
    """Base configuration for all device child admins"""
    base_model = Device
    inlines = [DeviceConfigInline]
    
    base_fieldsets = (
        (_('Identification'), {
            'fields': ('code', 'name')
        }),
        (_('Location & Hardware'), {
            'fields': ('location', 'model', 'serial_number')
        }),
        (_('Network'), {
            'fields': ('ip_address', 'mac_address'),
            'classes': ('collapse',)
        }),
        (_('Status'), {
            'fields': ('is_active', 'is_online', 'last_seen')
        }),
        (_('User Assignment'), {
            'fields': ('assigned_user', 'assigned_date')
        }),
        (_('Notes'), {
            'fields': ('notes',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CashRegister)
class CashRegisterAdmin(DeviceChildAdmin):
    base_model = CashRegister
    show_in_index = True
    
    list_display = ['code', 'name', 'location', 'is_active', 'is_online', 'has_open_session']
    search_fields = ['code', 'name', 'location']
    
    def has_open_session(self, obj):
        return obj.has_open_session
    has_open_session.boolean = True
    has_open_session.short_description = _('Has Open Session')


@admin.register(PriceChecker)
class PriceCheckerAdmin(DeviceChildAdmin):
    base_model = PriceChecker
    show_in_index = True
    
    list_display = ['code', 'name', 'location', 'is_active', 'is_online', 'display_promotions', 'timeout_seconds']
    search_fields = ['code', 'name', 'location']
    list_filter = ['display_promotions']
    
    fieldsets = DeviceChildAdmin.base_fieldsets + (
        (_('Price Checker Settings'), {
            'fields': ('display_promotions', 'timeout_seconds')
        }),
    )


@admin.register(StockTerminal)
class StockTerminalAdmin(DeviceChildAdmin):
    base_model = StockTerminal
    show_in_index = True
    
    list_display = ['code', 'name', 'location', 'is_active', 'is_online', 'can_receive_shipments', 'require_photo']
    search_fields = ['code', 'name', 'location']
    list_filter = ['can_receive_shipments', 'require_photo']
    
    fieldsets = DeviceChildAdmin.base_fieldsets + (
        (_('Stock Terminal Settings'), {
            'fields': ('can_receive_shipments', 'require_photo')
        }),
    )


@admin.register(Device)
class DeviceParentAdmin(PolymorphicParentModelAdmin):
    """Parent admin for polymorphic Device model"""
    base_model = Device
    child_models = (CashRegister, PriceChecker, StockTerminal)
    list_filter = (PolymorphicChildModelFilter, 'is_active', 'is_online')
    list_display = ['code', 'name', 'get_device_type', 'location', 'is_active', 'is_online', 'last_seen']
    search_fields = ['code', 'name', 'location']
    
    def get_device_type(self, obj):
        return obj.__class__.__name__
    get_device_type.short_description = _('Type')


@admin.register(DeviceConfig)
class DeviceConfigAdmin(admin.ModelAdmin):
    list_display = ['device', 'key', 'value', 'updated_at']
    list_filter = ['key']
    search_fields = ['device__code', 'device__name', 'key', 'value']
    readonly_fields = ['created_at', 'updated_at']

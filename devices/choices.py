from django.db.models.enums import TextChoices
from django.utils.translation import gettext_lazy as _


class DeviceType(TextChoices):
    """Types of devices in the system"""
    CASH_REGISTER = 'CASH_REGISTER', _('Cash Register')
    PRICE_CHECKER = 'PRICE_CHECKER', _('Price Checker')
    STOCK_TERMINAL = 'STOCK_TERMINAL', _('Stock Terminal')
    ADMIN_DEVICE = 'ADMIN_DEVICE', _('Admin Device')
    OTHER = 'OTHER', _('Other')


class DeviceStatus(TextChoices):
    """Online/Offline status"""
    ONLINE = 'ONLINE', _('Online')
    OFFLINE = 'OFFLINE', _('Offline')
    MAINTENANCE = 'MAINTENANCE', _('Maintenance')

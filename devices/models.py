from django.db import models
from polymorphic.models import PolymorphicModel
from django.db.models.fields import CharField, BooleanField, DateTimeField, GenericIPAddressField, TextField
from django.db.models.fields.related import ForeignKey
from django.db.models.deletion import SET_NULL, CASCADE
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.exceptions import ValidationError

from cash.choices import SessionStatus


class Device(PolymorphicModel):
    """
    Base polymorphic model for all devices in the system.
    Child classes: CashRegister, PriceChecker, StockTerminal
    """
    # Identification
    code = CharField(max_length=50, unique=True, verbose_name=_('code'), 
                    help_text=_('Unique identifier for the device'))
    name = CharField(max_length=200, verbose_name=_('name'))
    
    # Location
    location = CharField(max_length=200, null=True, blank=True, verbose_name=_('location'),
                        help_text=_('Physical location of the device'))
    
    # Hardware Information
    model = CharField(max_length=100, null=True, blank=True, verbose_name=_('model'))
    serial_number = CharField(max_length=100, null=True, blank=True, verbose_name=_('serial number'))
    
    # Network Information
    ip_address = GenericIPAddressField(null=True, blank=True, verbose_name=_('IP address'))
    mac_address = CharField(max_length=17, null=True, blank=True, verbose_name=_('MAC address'),
                           help_text=_('Format: XX:XX:XX:XX:XX:XX'))
    
    # Status
    is_active = BooleanField(default=True, verbose_name=_('is active'),
                            help_text=_('Whether the device is active in the system'))
    is_online = BooleanField(default=False, verbose_name=_('is online'))
    last_seen = DateTimeField(null=True, blank=True, verbose_name=_('last seen'),
                             help_text=_('Last time the device checked in'))
    
    # Branch Assignment
    branch = ForeignKey('core.Branch', null=True, blank=True,
                       on_delete=SET_NULL, related_name='devices',
                       verbose_name=_('branch'),
                       help_text=_('Branch where this device is located'))
    
    # User Assignment
    assigned_user = ForeignKey(get_user_model(), null=True, blank=True, 
                              on_delete=SET_NULL, related_name='assigned_devices',
                              verbose_name=_('assigned user'))
    assigned_date = DateTimeField(null=True, blank=True, verbose_name=_('assigned date'))
    
    # Notes
    notes = TextField(null=True, blank=True, verbose_name=_('notes'))
    
    # Audit timestamps
    created_at = DateTimeField(auto_now_add=True, verbose_name=_('created at'))
    updated_at = DateTimeField(auto_now=True, verbose_name=_('updated at'))
    
    class Meta:
        verbose_name = _('device')
        verbose_name_plural = _('devices')
        ordering = ['name']
        indexes = [
            models.Index(fields=['polymorphic_ctype']),
            models.Index(fields=['code']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f'{self.name} ({self.code})'
    
    def heartbeat(self):
        """Update last_seen timestamp and set device as online"""
        self.last_seen = timezone.now()
        self.is_online = True
        self.save(update_fields=['last_seen', 'is_online'])
    
    def assign_to_user(self, user):
        """Assign device to a user"""
        self.assigned_user = user
        self.assigned_date = timezone.now()
        self.save(update_fields=['assigned_user', 'assigned_date'])
    
    def unassign_user(self):
        """Remove user assignment"""
        self.assigned_user = None
        self.assigned_date = None
        self.save(update_fields=['assigned_user', 'assigned_date'])
    
    def get_config(self, key, default=None):
        """Get a configuration value"""
        try:
            config = self.configurations.get(key=key)
            return config.value
        except DeviceConfig.DoesNotExist:
            return default
    
    def set_config(self, key, value):
        """Set a configuration value"""
        config, created = self.configurations.update_or_create(
            key=key,
            defaults={'value': value}
        )
        return config
    
    def clean(self):
        """Validate model"""
        super().clean()
        
        # Validate MAC address format if provided
        if self.mac_address:
            import re
            mac_pattern = r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'
            if not re.match(mac_pattern, self.mac_address):
                raise ValidationError({
                    'mac_address': _('Invalid MAC address format. Use XX:XX:XX:XX:XX:XX')
                })


class CashRegister(Device):
    """
    Cash register device - inherits all Device fields.
    Used for processing sales and managing cash sessions.
    """
    
    class Meta:
        verbose_name = _('cash register')
        verbose_name_plural = _('cash registers')
    
    @property
    def current_session(self):
        """Returns the current open session for this cash register, if any"""
        return self.sessions.filter(status=SessionStatus.OPEN).first()
    
    @property
    def has_open_session(self):
        """Check if this cash register has an open session"""
        return self.sessions.filter(status=SessionStatus.OPEN).exists()


class PriceChecker(Device):
    """
    Price checking terminal for customers.
    Allows scanning products to view prices and promotions.
    """
    display_promotions = BooleanField(default=True, verbose_name=_('display promotions'))
    timeout_seconds = models.IntegerField(default=30, verbose_name=_('timeout seconds'),
                                         help_text=_('Idle timeout in seconds'))
    
    class Meta:
        verbose_name = _('price checker')
        verbose_name_plural = _('price checkers')


class StockTerminal(Device):
    """
    Stock management terminal for warehouse staff.
    Used for inventory adjustments and receiving shipments.
    """
    can_receive_shipments = BooleanField(default=True, verbose_name=_('can receive shipments'))
    require_photo = BooleanField(default=False, verbose_name=_('require photo'),
                                help_text=_('Require photo proof for stock adjustments'))
    
    class Meta:
        verbose_name = _('stock terminal')
        verbose_name_plural = _('stock terminals')


class DeviceConfig(models.Model):
    """
    Configuration key-value pairs for devices
    Allows device-specific settings without JSONField
    """
    device = ForeignKey(Device, on_delete=CASCADE, related_name='configurations', 
                       verbose_name=_('device'))
    key = CharField(max_length=100, verbose_name=_('key'),
                   help_text=_('Configuration key (e.g., "display_promotions", "timeout_seconds")'))
    value = CharField(max_length=500, verbose_name=_('value'),
                     help_text=_('Configuration value'))
    
    created_at = DateTimeField(auto_now_add=True, verbose_name=_('created at'))
    updated_at = DateTimeField(auto_now=True, verbose_name=_('updated at'))
    
    class Meta:
        verbose_name = _('device configuration')
        verbose_name_plural = _('device configurations')
        unique_together = [['device', 'key']]
        ordering = ['device', 'key']
    
    def __str__(self):
        return f'{self.device.code} - {self.key}: {self.value}'



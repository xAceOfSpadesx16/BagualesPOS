from __future__ import annotations
from typing import TYPE_CHECKING
from django.db.models import Model, TextChoices
from django.db.models.fields import CharField, IntegerField, BooleanField, DateTimeField, EmailField, DecimalField
from django.db.models.fields.files import ImageField
from django.db.models.fields.related import ForeignKey, ManyToManyField
from django.db.models.deletion import SET_NULL, CASCADE
from django.db.models.indexes import Index
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from django_multitenant.models import TenantModel

from utils import PhoneNumberField
from utils.formats import formatted_integer

from django.conf import settings

if TYPE_CHECKING:
    from inventory.models import Inventory

class Category(TenantModel):
    tenant_id = 'company_id'
    
    company = ForeignKey('core.Company', on_delete=CASCADE, related_name='categories', verbose_name=_('company'), null=True, blank=True)
    name = CharField(_('name'), max_length=50)
    created_at = DateTimeField(auto_now_add=True, editable=False)
    updated_at = DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')
        ordering = ['name']
        unique_together = [['company', 'name']]
        indexes = [
            Index(fields=['name'], name='category_name_idx'),
        ]


class Subcategory(TenantModel):
    tenant_id = 'company_id'
    
    company = ForeignKey('core.Company', on_delete=CASCADE, related_name='subcategories', verbose_name=_('company'), null=True, blank=True)
    name = CharField(_('name'), max_length=50)
    created_at = DateTimeField(auto_now_add=True, editable=False)
    updated_at = DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('subcategory')
        verbose_name_plural = _('subcategories')
        unique_together = [['company', 'name']]
        indexes = [
            Index(fields=['name'], name='subcategory_name_idx'),
        ]

class Season(TenantModel):
    tenant_id = 'company_id'
    
    company = ForeignKey('core.Company', on_delete=CASCADE, related_name='seasons', verbose_name=_('company'), null=True, blank=True)
    name = CharField(_('name'), max_length=50)
    created_at = DateTimeField(auto_now_add=True, editable=False)
    updated_at = DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = _('season')
        verbose_name_plural = _('seasons')
        unique_together = [['company', 'name']]
        indexes = [
            Index(fields=['name'], name='season_name_idx'),
        ]


class Color(TenantModel):
    tenant_id = 'company_id'
    
    company = ForeignKey('core.Company', on_delete=CASCADE, related_name='colors', verbose_name=_('company'), null=True, blank=True)
    name = CharField(_('name'),max_length=50)
    code = CharField(_('code'), max_length=7)
    created_at = DateTimeField(auto_now_add=True, editable=False)
    updated_at = DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = _('color')
        verbose_name_plural = _( 'colors')
        unique_together = [['company', 'name']]
        indexes = [
            Index(fields=['name'], name='color_name_idx'),
        ]


class Gender(TenantModel):
    tenant_id = 'company_id'
    
    company = ForeignKey('core.Company', on_delete=CASCADE, related_name='genders', verbose_name=_('company'), null=True, blank=True)
    name = CharField(_('name'), max_length=50)
    created_at = DateTimeField(auto_now_add=True, editable=False)
    updated_at = DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = _('gender')
        verbose_name_plural = _('genders')
        unique_together = [['company', 'name']]
        indexes = [
            Index(fields=['name'], name='gender_name_idx'),
        ]
    
class LetterSize(TenantModel):
    tenant_id = 'company_id'
    
    company = ForeignKey('core.Company', on_delete=CASCADE, related_name='letter_sizes', verbose_name=_('company'), null=True, blank=True)
    short_name = CharField(_('short name'), max_length=4)
    name = CharField(_('name'), max_length=50)
    created_at = DateTimeField(auto_now_add=True, editable=False)
    updated_at = DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = _('size')
        verbose_name_plural = _('sizes')
        unique_together = [['company', 'name'], ['company', 'short_name']]
        indexes = [
            Index(fields=['name'], name='letter_size_name_idx'),
        ]


class Materials(TenantModel):
    tenant_id = 'company_id'
    
    company = ForeignKey('core.Company', on_delete=CASCADE, related_name='materials', verbose_name=_('company'), null=True, blank=True)
    name = CharField(_('name'),max_length=50)
    created_at = DateTimeField(auto_now_add=True, editable=False)
    updated_at = DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = _('material')
        verbose_name_plural = _('materials')
        unique_together = [['company', 'name']]
        indexes = [
            Index(fields=['name'], name='material_name_idx'),
        ]


class Supplier(TenantModel):
    tenant_id = 'company_id'
    
    company = ForeignKey('core.Company', on_delete=CASCADE, related_name='suppliers', verbose_name=_('company'), null=True, blank=True)
    name = CharField(_('name'), max_length=50)
    phone_number = PhoneNumberField(null=True, blank=True, verbose_name=_( 'phone number'))
    email = EmailField(_('email'), null=True, blank=True)
    address = CharField(_('address'), max_length=100, null=True, blank=True)

    created_at = DateTimeField(auto_now_add=True, editable=False)
    updated_at = DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = _('supplier')
        verbose_name_plural = _('suppliers')
        unique_together = [['company', 'name']]
        indexes = [
            Index(fields=['name'], name='supplier_name_idx'),
        ]


class Brand(TenantModel):
    tenant_id = 'company_id'
    
    company = ForeignKey('core.Company', on_delete=CASCADE, related_name='brands', verbose_name=_('company'), null=True, blank=True)
    name = CharField(_('name'), max_length=50)
    supplier = ForeignKey(Supplier, on_delete=SET_NULL, null=True, blank=True, verbose_name=_( 'supplier'))
    logo = ImageField(_('logo'), upload_to='brands/', null=True, blank=True)
    created_at = DateTimeField(auto_now_add=True, editable=False)
    updated_at = DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = _('brand')
        verbose_name_plural = _('brands')
        ordering = ['name']
        unique_together = [['company', 'name']]
        indexes = [
            Index(fields=['name'], name='brand_name_idx'),
        ]


class Product(TenantModel):
    tenant_id = 'company_id'
    
    inventory: Inventory
    company = ForeignKey('core.Company', on_delete=CASCADE, related_name='products', verbose_name=_('company'), null=True, blank=True)
    name = CharField(_('name'),max_length=50)
    numeric_size = IntegerField(_('numeric size'), null=True, blank=True)
    cost_price = DecimalField(_('cost price'), max_digits=10, decimal_places=2)
    sale_price = DecimalField(_('sale price'), max_digits=10, decimal_places=2)
    internal_code = CharField(_('internal code'), max_length=50, editable=False, null=True, blank=True)
    details = CharField(_('details'),max_length=64, null=True, blank=True)
    image = ImageField(_('image'),upload_to='products/', null=True, blank=True)
    is_active = BooleanField(_('active'),default=True)
    gender = ForeignKey(Gender, on_delete=SET_NULL, null=True, verbose_name=_('gender'))
    letter_size = ForeignKey(LetterSize, on_delete=SET_NULL, null=True, blank=True, verbose_name=_('letter size'))
    material = ForeignKey(Materials, on_delete=SET_NULL, null=True, blank=True, verbose_name=_('material'))
    color = ForeignKey(Color, on_delete=SET_NULL, null=True, verbose_name=_('color'))
    brand = ForeignKey(Brand, on_delete=SET_NULL, null=True, verbose_name=_('brand'))
    category = ForeignKey(Category, on_delete=SET_NULL, null=True, verbose_name=_('category'))
    subcategories = ManyToManyField(Subcategory, blank=True, related_name='products', verbose_name=_('subcategories'))
    season = ForeignKey(Season, on_delete=SET_NULL, null=True, verbose_name=_('season'))
    created_at = DateTimeField(_('created at'), auto_now_add=True, editable=False)
    updated_at = DateTimeField(_('updated at'), auto_now=True)
    is_deleted = BooleanField(_('deleted'), default=False)
    deleted_at = DateTimeField(_('deleted at'), null=True, blank=True)

    def __str__(self):
        return f'{self.name} - {self.brand.name}'
    
    @property
    def formatted_cost_price(self):
        return formatted_integer(self.cost_price)
        
    @property
    def formatted_sale_price(self):
        return formatted_integer(self.sale_price)
    
    def soft_delete(self, *args, **kwargs):
        self.is_deleted = True
        self.deleted_at = now()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _('product')
        verbose_name_plural = _('products')
        ordering = ['name']
        indexes = [
            Index(fields=['name'], name='product_name_idx'),
            Index(fields=['numeric_size'], name='product_numeric_size_idx'),
            Index(fields=['internal_code'], name='product_internal_code_idx'),
            Index(fields=['details'], name='product_details_idx'),
        ]


class PriceHistory(TenantModel):
    """Registro inmutable de cambios de precio en productos."""
    tenant_id = 'company_id'

    class PriceField(TextChoices):
        SALE_PRICE = 'sale_price', _('Sale Price')
        COST_PRICE = 'cost_price', _('Cost Price')

    class Source(TextChoices):
        MANUAL = 'MANUAL', _('Manual')
        BULK_UPDATE = 'BULK_UPDATE', _('Bulk Update')

    company = ForeignKey('core.Company', on_delete=CASCADE, related_name='price_histories', verbose_name=_('company'))
    product = ForeignKey(Product, on_delete=CASCADE, related_name='price_history', verbose_name=_('product'))
    field = CharField(max_length=20, choices=PriceField.choices, verbose_name=_('field'))
    old_value = DecimalField(max_digits=12, decimal_places=2, verbose_name=_('old value'))
    new_value = DecimalField(max_digits=12, decimal_places=2, verbose_name=_('new value'))
    change_percentage = DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name=_('change percentage'))
    reason = CharField(max_length=255, blank=True, default='', verbose_name=_('reason'))
    source = CharField(max_length=20, choices=Source.choices, default=Source.MANUAL, verbose_name=_('source'))
    changed_by = ForeignKey(settings.AUTH_USER_MODEL, on_delete=SET_NULL, null=True, verbose_name=_('changed by'))
    created_at = DateTimeField(auto_now_add=True, verbose_name=_('created at'))

    class Meta:
        verbose_name = _('price history')
        verbose_name_plural = _('price histories')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.product} - {self.field}: {self.old_value} → {self.new_value}'
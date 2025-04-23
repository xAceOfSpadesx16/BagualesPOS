from __future__ import annotations
from typing import TYPE_CHECKING
from django.db.models import Model
from django.db.models.fields import CharField, IntegerField, BooleanField, DateTimeField, EmailField
from django.db.models.fields.files import ImageField
from django.db.models.fields.related import ForeignKey
from django.db.models.deletion import SET_NULL
from django.db.models.indexes import Index
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from utils import PhoneNumberField
from utils.formats import formatted_integer

if TYPE_CHECKING:
    from inventory.models import Inventory

class Category(Model):
    name = CharField(_('name'), max_length=50)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')
        indexes = [
            Index(fields=['name'], name='category_name_idx'),
        ]


class Season(Model):
    name = CharField(_('name'), max_length=50)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = _('season')
        verbose_name_plural = _('seasons')
        indexes = [
            Index(fields=['name'], name='season_name_idx'),
        ]


class Color(Model):
    name = CharField(_('name'),max_length=50)
    code = CharField(_('code'), max_length=7)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = _('color')
        verbose_name_plural = _( 'colors')
        indexes = [
            Index(fields=['name'], name='color_name_idx'),
        ]


class Gender(Model):
    name = CharField(_('name'), max_length=50)
    created_at = DateTimeField(auto_now_add=True, editable=False)
    updated_at = DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = _('gender')
        verbose_name_plural = _('genders')
        indexes = [
            Index(fields=['name'], name='gender_name_idx'),
        ]
    
class LetterSize(Model):
    name = CharField(_('name'), max_length=4)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = _('size')
        verbose_name_plural = _('sizes')
        indexes = [
            Index(fields=['name'], name='letter_size_name_idx'),
        ]


class Materials(Model):
    name = CharField(_('name'),max_length=50)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = _('material')
        verbose_name_plural = _('materials')
        indexes = [
            Index(fields=['name'], name='material_name_idx'),
        ]


class Supplier(Model):
    name = CharField(_('name'), max_length=50)
    phone_number = PhoneNumberField(null=True, verbose_name=_( 'phone number'))
    email = EmailField(_('email'), null=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = _('supplier')
        verbose_name_plural = _('suppliers')
        indexes = [
            Index(fields=['name'], name='supplier_name_idx'),
        ]


class Brand(Model):
    name = CharField(_('name'), max_length=50)
    supplier = ForeignKey(Supplier, on_delete=SET_NULL, null=True, verbose_name=_( 'supplier'))
    logo = ImageField(_('logo'), upload_to='brands/', null=True, blank=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = _('brand')
        verbose_name_plural = _('brands')
        indexes = [
            Index(fields=['name'], name='brand_name_idx'),
        ]


class Product(Model):
    inventory: Inventory
    name = CharField(_('name'),max_length=50)
    numeric_size = IntegerField(_('numeric size'), null=True, blank=True)
    cost_price = IntegerField(_('cost price'))
    sale_price = IntegerField(_('sale price'))
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
        indexes = [
            Index(fields=['name'], name='product_name_idx'),
            Index(fields=['numeric_size'], name='product_numeric_size_idx'),
            Index(fields=['internal_code'], name='product_internal_code_idx'),
            Index(fields=['details'], name='product_details_idx'),
        ]
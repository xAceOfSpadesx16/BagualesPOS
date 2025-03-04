from __future__ import annotations
from typing import TYPE_CHECKING
from django.db.models import Model
from django.db.models.fields import CharField, IntegerField, BooleanField, DateTimeField, EmailField
from django.db.models.fields.files import ImageField
from django.db.models.fields.related import ForeignKey
from django.db.models.deletion import SET_NULL
from django.db.models.indexes import Index
from django.utils.text import slugify

from utils import PhoneNumberField

if TYPE_CHECKING:
    from inventory.models import Inventory

class Category(Model):
    name = CharField(max_length=50)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        indexes = [
            Index(fields=['name'], name='category_name_idx'),
        ]


class Season(Model):
    name = CharField(max_length=50)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Temporada'
        verbose_name_plural = 'Temporadas'
        indexes = [
            Index(fields=['name'], name='season_name_idx'),
        ]


class Color(Model):
    name = CharField(max_length=50)
    code = CharField(max_length=6)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Color'
        verbose_name_plural = 'Colores'
        indexes = [
            Index(fields=['name'], name='color_name_idx'),
        ]


class Gender(Model):
    name = CharField(max_length=50)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Género'
        verbose_name_plural = 'Géneros'
        indexes = [
            Index(fields=['name'], name='gender_name_idx'),
        ]
    
class LetterSize(Model):
    name = CharField(max_length=4)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Talle'
        verbose_name_plural = 'Talles'
        indexes = [
            Index(fields=['name'], name='letter_size_name_idx'),
        ]


class Materials(Model):
    name = CharField(max_length=50)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Material'
        verbose_name_plural = 'Materiales'
        indexes = [
            Index(fields=['name'], name='material_name_idx'),
        ]


class Supplier(Model):
    name = CharField(max_length=50)
    phone_number = PhoneNumberField(null=True)
    email = EmailField(null=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'
        indexes = [
            Index(fields=['name'], name='supplier_name_idx'),
        ]


class Brand(Model):
    name = CharField(max_length=50)
    supplier = ForeignKey(Supplier, on_delete=SET_NULL, null=True)
    logo = ImageField(upload_to='brands/', null=True, blank=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Marca'
        verbose_name_plural = 'Marcas'
        indexes = [
            Index(fields=['name'], name='brand_name_idx'),
        ]


class Product(Model):
    inventory: Inventory
    name = CharField(max_length=50)
    numeric_size = IntegerField(null=True)
    cost_price = IntegerField()
    sale_price = IntegerField()
    internal_code = CharField(max_length=50, editable=False, null=True, blank=True)
    details = CharField(max_length=64, null=True)
    image = ImageField(upload_to='products/', null=True, blank=True)
    is_active = BooleanField(default=True)
    gender = ForeignKey(Gender, on_delete=SET_NULL, null=True)
    letter_size = ForeignKey(LetterSize, on_delete=SET_NULL, null=True, blank=True)
    material = ForeignKey(Materials, on_delete=SET_NULL, null=True)
    color = ForeignKey(Color, on_delete=SET_NULL, null=True)
    brand = ForeignKey(Brand, on_delete=SET_NULL, null=True)
    category = ForeignKey(Category, on_delete=SET_NULL, null=True)
    season = ForeignKey(Season, on_delete=SET_NULL, null=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.name} - {self.gender}'
    
    def save(self, *args, **kwargs):
        if not self.internal_code:
            category_prefix = slugify(self.category.name[:3]).upper()
            self.internal_code = f"{category_prefix}-{self.pk}"
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        indexes = [
            Index(fields=['name'], name='product_name_idx'),
            Index(fields=['numeric_size'], name='product_numeric_size_idx'),
            Index(fields=['internal_code'], name='product_internal_code_idx'),
            Index(fields=['details'], name='product_details_idx'),
        ]
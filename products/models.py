from __future__ import annotations
from typing import TYPE_CHECKING
from django.db.models import Model, SET_NULL
from django.db.models.fields import CharField, IntegerField, BooleanField, DateTimeField, EmailField
from django.db.models.fields.files import ImageField
from django.db.models.fields.related import ForeignKey
from utils import PhoneNumberField

if TYPE_CHECKING:
    from inventory.models import Inventory

class Color(Model):
    name = CharField(max_length=50)
    code = CharField(max_length=6)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Color'
        verbose_name_plural = 'Colores'

class Gender(Model):
    name = CharField(max_length=50)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Género'
        verbose_name_plural = 'Géneros'
    
class LetterSize(Model):
    name = CharField(max_length=4)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Talle'
        verbose_name_plural = 'Talles'

class Materials(Model):
    name = CharField(max_length=50)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Material'
        verbose_name_plural = 'Materiales'

class Supplier(Model):
    name = CharField(max_length=50)
    phone_number = PhoneNumberField(null=True)
    email = EmailField(null=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'

class Product(Model):
    inventory: Inventory
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('U', 'Unisex'),
    )
    name = CharField(max_length=50)
    gender = CharField(max_length=1, choices=GENDER_CHOICES)
    numeric_size = IntegerField(null=True)
    letter_size = ForeignKey(LetterSize, on_delete=SET_NULL, null=True)
    material = ForeignKey(Materials, on_delete=SET_NULL, null=True)
    color = ForeignKey(Color, on_delete=SET_NULL, null=True)
    supplier = ForeignKey(Supplier, on_delete=SET_NULL, null=True)
    cost_price = IntegerField()
    sale_price = IntegerField()
    details = CharField(max_length=64, null=True)
    image = ImageField(upload_to='products/', null=True)
    is_active = BooleanField()
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.name} - {self.gender}'
    
    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
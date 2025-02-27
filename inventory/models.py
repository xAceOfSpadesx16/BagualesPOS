from django.db.models import Model, CASCADE
from django.db.models.fields import IntegerField
from django.db.models.fields.related import OneToOneField

from products.models import Product

class Inventory(Model):
    product = OneToOneField(Product, on_delete=CASCADE, related_name='inventory')
    quantity = IntegerField()

    def __str__(self):
        return f'{self.product} - {self.quantity}'
    
    class Meta:
        verbose_name = 'Inventario'
        verbose_name_plural = 'Inventarios'

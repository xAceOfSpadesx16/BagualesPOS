from django.db.models import Model, CASCADE
from django.db.models.fields import IntegerField
from django.db.models.fields.related import OneToOneField

from inventory.managers import InventoryManager

from products.models import Product

class Inventory(Model):
    product = OneToOneField(Product, on_delete=CASCADE, related_name='inventory')
    quantity = IntegerField(default=0)

    objects: InventoryManager = InventoryManager()

    def __str__(self):
        return f'{self.product} - {self.quantity}'
    
    def update_quantity(self, quantity: int) -> None:
        """ Quantity += new quantity """
        self.quantity += quantity
        self.save()
        
    class Meta:
        verbose_name = 'Inventario'
        verbose_name_plural = 'Inventarios'

from django.db.models import Model, CASCADE
from django.db.models.fields import IntegerField
from django.db.models.fields.related import OneToOneField
from django.utils.translation import gettext_lazy as _

from inventory.managers import InventoryManager

from products.models import Product

class Inventory(Model):
    product = OneToOneField(Product, on_delete=CASCADE, related_name='inventory', verbose_name=_('product'))
    quantity = IntegerField(default=0, verbose_name=_('quantity'))

    objects: InventoryManager = InventoryManager()

    def __str__(self):
        return f'{self.product} - {self.quantity}'
    
    def update_quantity(self, quantity: int) -> None:
        """ Quantity += new quantity """
        self.quantity += quantity
        self.save()
        
    class Meta:
        verbose_name = _('inventory')
        verbose_name_plural = _('inventories')

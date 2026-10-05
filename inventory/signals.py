from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.transaction import atomic

from core.models import Branch
from products.models import Product
from inventory.models import Inventory

@receiver(post_save, sender=Branch)
@atomic
def create_branch_stock(sender, instance: Branch, created: bool, **kwargs):
    """
    When a new branch is created, generate 0-stock inventory records
    for all existing products in the company.
    """
    if created and instance.company:
        products = Product.objects.filter(company=instance.company)
        inventories = [
            Inventory(product=product, company=instance.company, branch=instance, quantity=0)
            for product in products
        ]
        
        if inventories:
            Inventory.objects.bulk_create(inventories)

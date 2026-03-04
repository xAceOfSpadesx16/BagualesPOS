from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils.text import slugify
from django.db.transaction import atomic

from products.models import Product
from inventory.models import Inventory

@receiver(post_save, sender=Product)
def set_internal_code(sender, instance: Product, created: bool, **kwargs):
    if created and not instance.internal_code:
        # Only set internal code if category is present
        if instance.category:
            category_prefix = slugify(instance.category.name[:3]).upper()
            instance.internal_code = f"{category_prefix}-{instance.pk}"
            instance.save(update_fields=['internal_code'])

@receiver(post_save, sender=Product)
@atomic
def create_stock(sender, instance: Product, created: bool, **kwargs):
    if created and instance.company:
        from core.models import Branch
        
        branches = Branch.objects.filter(company=instance.company)
        inventories = [
            Inventory(product=instance, company=instance.company, branch=branch, quantity=0)
            for branch in branches
        ]
        
        if inventories:
            Inventory.objects.bulk_create(inventories)



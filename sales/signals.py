from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from sales.models import SaleDetail

receiver(post_save, sender=SaleDetail)
def update_stock(sender, instance: SaleDetail, created: bool, **kwargs):
    product_stock = instance.product.inventory.quantity
    if created:
        product_stock -= instance.quantity
    else:

        old_record = SaleDetail.objects.get(pk=instance.pk)
        product_stock -= instance.quantity - old_record.quantity

    product_stock.save()


receiver(post_delete, sender=SaleDetail)
def update_stock(sender, instance: SaleDetail, **kwargs):
    instance.product.inventory.quantity += instance.quantity
    instance.product.inventory.save()
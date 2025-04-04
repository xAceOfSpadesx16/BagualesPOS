from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.transaction import atomic
from django.db.models.aggregates import Sum
from django.db.models.expressions import F

from sales.models import SaleDetail

@receiver(post_save, sender=SaleDetail)
@atomic
def update_stock(sender, instance: SaleDetail, created: bool, **kwargs):

    stock = instance.product.inventory
    if created:
        stock.quantity -= instance.quantity
    else:
        old_record = SaleDetail.objects.get(pk=instance.pk)
        stock.quantity -= instance.quantity - old_record.quantity
    stock.save()

@receiver(post_save, sender = SaleDetail)
@receiver(post_delete, sender = SaleDetail)
@atomic
def update_sale_total(sender, instance: SaleDetail, **kwargs):
    sale = instance.order
    total_price_details = SaleDetail.objects.filter(order=sale).aggregate(total_price = Sum(F('sale_price') * F('quantity')))['total_price'] or 0
    sale.total_amount = total_price_details
    sale.save()


@receiver(post_delete, sender=SaleDetail)
@atomic
def update_stock(sender, instance: SaleDetail, **kwargs):
    if instance.product:
        instance.product.inventory.quantity += instance.quantity
        instance.product.inventory.save()

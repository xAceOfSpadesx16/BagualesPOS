from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.db.transaction import atomic
from django.db.models.aggregates import Sum
from django.db.models.expressions import F

from sales.models import SaleDetail

@receiver(pre_save, sender=SaleDetail)
def cache_old_quantity(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = SaleDetail.objects.get(pk=instance.pk)
            instance._old_quantity = old_instance.quantity
        except SaleDetail.DoesNotExist:
            instance._old_quantity = 0
    else:
        instance._old_quantity = 0

@receiver(post_save, sender=SaleDetail)
@atomic
def update_stock_save(sender, instance: SaleDetail, created: bool, **kwargs):

    stock = instance.product.inventory
    stock.quantity -= (instance.quantity - instance._old_quantity)
    stock.save()
    instance.product.save()


@receiver(post_delete, sender=SaleDetail)
@atomic
def update_stock_delete(sender, instance: SaleDetail, **kwargs):
    if instance.product:
        instance.product.inventory.quantity += instance.quantity
        instance.product.inventory.save()
        instance.product.save()

@receiver(post_save, sender = SaleDetail)
@receiver(post_delete, sender = SaleDetail)
@atomic
def update_sale_total(sender, instance: SaleDetail, **kwargs):
    sale = instance.order
    total_price_details = SaleDetail.objects.filter(order=sale).aggregate(total_price = Sum(F('sale_price') * F('quantity')))['total_price'] or 0
    sale.total_amount = total_price_details
    sale.save()


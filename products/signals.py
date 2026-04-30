from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.utils.text import slugify
from django.db.transaction import atomic

from products.models import Product, PriceHistory
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


# Cache de precios previos antes de guardar
@receiver(pre_save, sender=Product)
def cache_old_prices(sender, instance: Product, **kwargs):
    """Almacena los precios previos para detectar cambios en post_save."""
    if instance.pk:
        try:
            old = Product.objects.get(pk=instance.pk)
            instance._old_sale_price = old.sale_price
            instance._old_cost_price = old.cost_price
        except Product.DoesNotExist:
            instance._old_sale_price = None
            instance._old_cost_price = None
    else:
        instance._old_sale_price = None
        instance._old_cost_price = None


@receiver(post_save, sender=Product)
def track_price_changes(sender, instance: Product, created: bool, **kwargs):
    """Crea registros en PriceHistory cuando cambian los precios."""
    if created:
        return

    old_sale = getattr(instance, '_old_sale_price', None)
    old_cost = getattr(instance, '_old_cost_price', None)

    if old_sale is not None and instance.sale_price != old_sale:
        change_pct = None
        if old_sale and old_sale != 0:
            change_pct = round(((instance.sale_price - old_sale) / old_sale) * 100, 2)

        PriceHistory.objects.create(
            company=instance.company,
            product=instance,
            field=PriceHistory.PriceField.SALE_PRICE,
            old_value=old_sale,
            new_value=instance.sale_price,
            change_percentage=change_pct,
            source=PriceHistory.Source.MANUAL,
        )

    if old_cost is not None and instance.cost_price != old_cost:
        change_pct = None
        if old_cost and old_cost != 0:
            change_pct = round(((instance.cost_price - old_cost) / old_cost) * 100, 2)

        PriceHistory.objects.create(
            company=instance.company,
            product=instance,
            field=PriceHistory.PriceField.COST_PRICE,
            old_value=old_cost,
            new_value=instance.cost_price,
            change_percentage=change_pct,
            source=PriceHistory.Source.MANUAL,
        )



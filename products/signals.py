from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils.text import slugify

from products.models import Product

@receiver(post_save, sender=Product)
def set_internal_code(sender, instance: Product, created: bool, **kwargs):
    if created and not instance.internal_code:
        category_prefix = slugify(instance.category.name[:3]).upper()
        instance.internal_code = f"{category_prefix}-{instance.pk}"
        instance.save(update_fields=['internal_code'])
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.db.transaction import atomic
from django.db.models.aggregates import Sum
from django.db.models.expressions import F
from django.core.exceptions import ValidationError
from decimal import Decimal

from sales.models import SaleDetail, Sale
from sales.choices import PaymentStatus
from clients.models import CustomerBalanceRecord
from clients.choices import MovementType

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
    """Update inventory stock when SaleDetail is saved"""
    if not instance.product or not instance.order.branch:
        return
    
    from inventory.models import Inventory
    try:
        # Use select_for_update to prevent race conditions
        stock = Inventory.objects.select_for_update().get(product=instance.product, branch=instance.order.branch)
        
        quantity_diff = instance.quantity - instance._old_quantity
        stock.quantity -= quantity_diff
        
        # Check for negative stock (should have been prevented by clean(), but double-check)
        if stock.quantity < 0:
            raise ValidationError(f'Stock would become negative for product {instance.product} in branch {instance.order.branch}')
        
        stock.save()
    except Inventory.DoesNotExist:
        # If inventory is not set up, raise ValidationError
        raise ValidationError(f'Product {instance.product} does not have inventory in branch {instance.order.branch}')


@receiver(post_delete, sender=SaleDetail)
@atomic
def update_stock_delete(sender, instance: SaleDetail, **kwargs):
    """Restore inventory stock when SaleDetail is deleted"""
    if instance.product and instance.order.branch:
        from inventory.models import Inventory
        try:
            stock = Inventory.objects.select_for_update().get(product=instance.product, branch=instance.order.branch)
            stock.quantity += instance.quantity
            stock.save()
        except Inventory.DoesNotExist:
            pass

@receiver(post_save, sender = SaleDetail)
@receiver(post_delete, sender = SaleDetail)
@atomic
def update_sale_total(sender, instance: SaleDetail, **kwargs):
    """Recalculate sale total amount when details change"""
    sale = instance.order
    total_price_details = SaleDetail.objects.filter(order=sale).aggregate(
        total_price = Sum(F('sale_price') * F('quantity'))
    )['total_price'] or Decimal('0.00')
    sale.total_amount = total_price_details
    sale.save()


@receiver(post_save, sender=Sale)
@atomic
def integrate_sale_with_accounting(sender, instance: Sale, created: bool, **kwargs):
    """
    When a sale is closed with a client that has an active customer account,
    create a DEBIT record in their account.
    """
    # Only process if sale is closed and has a client
    if not instance.closed or not instance.client:
        return
    
    # Check if client has active customer account
    if not hasattr(instance.client, 'customer_account'):
        return
    
    customer_account = instance.client.customer_account
    if not customer_account.active:
        return
    
    # Check if we already created the account record (avoid duplicates)
    if instance.account_record_id:
        return
    
    # Create DEBIT record in customer account
    balance_record = CustomerBalanceRecord.objects.create(
        customer_account=customer_account,
        sale=instance,
        amount=instance.total_amount,
        movement_type=MovementType.DEBIT,
        notes=f'Venta #{instance.pk} - {instance.seller.get_full_name() if instance.seller else ""}',
        reference=f'SALE-{instance.pk}',
        created_by=instance.seller,
    )
    
    # Save the reference back to the sale
    instance.account_record_id = balance_record.pk
    Sale.objects.filter(pk=instance.pk).update(account_record_id=balance_record.pk)
    
    # Update payment status to PENDING for credit sales
    if instance.payment_status != PaymentStatus.PAID:
        Sale.objects.filter(pk=instance.pk).update(payment_status=PaymentStatus.PENDING)


@receiver(post_save, sender=Sale)
def update_payment_status_on_close(sender, instance: Sale, created: bool, **kwargs):
    """
    Update payment status when sale is closed.
    If not a credit sale (no customer account), mark as PAID.
    """
    if not instance.closed:
        return
    
    # If it's not a credit sale, mark as paid
    if not instance.is_credit_sale:
        if instance.payment_status != PaymentStatus.PAID:
            Sale.objects.filter(pk=instance.pk).update(payment_status=PaymentStatus.PAID)



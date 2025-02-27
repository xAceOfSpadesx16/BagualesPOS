from django.db.models.signals import post_save, post_delete
from django.db.transaction import atomic
from django.dispatch import receiver
from clients.models import CustomerBalanceRecord


@receiver(post_save, sender= CustomerBalanceRecord)
def update_client_balance(sender, instance: CustomerBalanceRecord, created: bool, **kwargs):
    with atomic():
        client = instance.client
        if created:
            client.balance += instance.amount
        else:
            old_record = CustomerBalanceRecord.objects.get(pk=instance.pk)
            client.balance += instance.amount - old_record.amount
        client.save()

@receiver(post_delete, sender=CustomerBalanceRecord)
def update_client_balance(sender, instance: CustomerBalanceRecord, **kwargs):
    with atomic():
        client = instance.client
        client.balance -= instance.amount
        client.save()
from django.db.models.signals import post_save, post_delete
from django.db.transaction import atomic
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from clients.models import CustomerBalanceRecord, CustomerAccount, Client

@receiver(post_save, sender=Client)
def create_current_account(sender, instance: Client, created: bool, **kwargs):
    """
    Automatically creates a CurrentAccount for a Client when the Client is created.
    """
    if created:
        with atomic():
            CustomerAccount.objects.create(client=instance, active=True, notes= f"{instance.name} {instance.last_name} - {_('Customer account.')}")

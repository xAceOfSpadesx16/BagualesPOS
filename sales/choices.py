from django.db.models.enums import TextChoices
from django.utils.translation import gettext_lazy as _

class PaymentStatus(TextChoices):
    PENDING = 'PENDING', _('Pending')
    PARTIAL = 'PARTIAL', _('Partial')
    PAID = 'PAID', _('Paid')

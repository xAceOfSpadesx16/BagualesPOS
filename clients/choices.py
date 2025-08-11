from django.db.models.enums import TextChoices
from django.utils.translation import gettext_lazy as _

class MovementType(TextChoices):
    CREDIT = 'CREDIT', _('Credit')
    DEBIT = 'DEBIT', _('Debit')
    ADJUSTMENT = 'ADJUSTMENT', _('Adjustment')
    REFUND = 'REFUND', _('Refund')
    REVERSAL = 'REVERSAL', _('Reversal')

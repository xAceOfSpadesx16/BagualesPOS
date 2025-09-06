from django.db.models.enums import TextChoices
from django.utils.translation import gettext_lazy as _

class MovementType(TextChoices):
    CREDIT = 'CREDIT', _('Credit')
    DEBIT = 'DEBIT', _('Debit')
    ADJUSTMENT = 'ADJUSTMENT', _('Adjustment')
    REFUND = 'REFUND', _('Refund')
    REVERSAL = 'REVERSAL', _('Reversal')

class BillingType(TextChoices):
    A = 'A', _('A')
    B = 'B', _('B')
    C = 'C', _('C')
    E = 'E', _('E')
    M = 'M', _('M')
    M2 = 'M2', _('M2')
    P = 'P', _('P')


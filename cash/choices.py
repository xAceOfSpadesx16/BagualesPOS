from django.db.models.enums import TextChoices
from django.utils.translation import gettext_lazy as _

class SessionStatus(TextChoices):
    OPEN = 'OPEN', _('Open')
    CLOSED = 'CLOSED', _('Closed')
    SUSPENDED = 'SUSPENDED', _('Suspended')

class MovementType(TextChoices):
    OPENING = 'OPENING', _('Opening Balance')
    CLOSING = 'CLOSING', _('Closing Balance')
    CASH_IN = 'CASH_IN', _('Cash In')
    CASH_OUT = 'CASH_OUT', _('Cash Out')

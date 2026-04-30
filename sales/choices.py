from django.db.models.enums import TextChoices
from django.utils.translation import gettext_lazy as _

class PaymentStatus(TextChoices):
    PENDING = 'PENDING', _('Pending')
    PARTIAL = 'PARTIAL', _('Partial')
    PAID = 'PAID', _('Paid')


class ReturnStatus(TextChoices):
    COMPLETED = 'COMPLETED', _('Completed')
    CANCELED = 'CANCELED', _('Canceled')


class ReturnReasonType(TextChoices):
    DEFECTIVE = 'DEFECTIVE', _('Defective / Damaged')
    WRONG_ITEM = 'WRONG_ITEM', _('Wrong Item')
    NOT_NEEDED = 'NOT_NEEDED', _('Not Needed')
    OTHER = 'OTHER', _('Other')


class ReturnCondition(TextChoices):
    RESALEABLE = 'RESALEABLE', _('Resaleable')
    DAMAGED = 'DAMAGED', _('Damaged')


class RefundMethod(TextChoices):
    CASH = 'CASH', _('Cash')
    STORE_CREDIT = 'STORE_CREDIT', _('Store Credit')
    ORIGINAL_METHOD = 'ORIGINAL_METHOD', _('Original Payment Method')

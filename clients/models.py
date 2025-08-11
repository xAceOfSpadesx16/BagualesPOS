from __future__ import annotations
from django.db.models import Model
from django.db.models.fields import CharField, DateTimeField, BooleanField, FloatField, TextField, DecimalField
from django.db.models.fields.related import ForeignKey, OneToOneField
from django.db.models.deletion import SET_NULL, PROTECT
from django.db.models.aggregates import Sum
from django.db.models.constraints import UniqueConstraint
from django.db.models.query_utils import Q
from django.db.models.enums import TextChoices
from django.db.models.indexes import Index
from django.core.validators import RegexValidator, validate_email
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS

from clients.managers import BalanceRecordsManager
from clients.choices import MovementType

from utils import PhoneNumberField
from utils.mixins import SoftDeleteMixin

class Client(Model):

    BILLING_TYPES = (
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('E', 'E'),
        ('M', 'M'),
        ('T', 'T'),
    )

    name = CharField(_('name'),max_length=50)
    last_name = CharField(_('last_name'), max_length=50)
    phone = PhoneNumberField(null=True, blank=True, verbose_name= _('phone number'))
    dni = CharField(max_length=9, verbose_name= _('dni'))
    cuit = CharField(max_length=13, null=True, validators=[RegexValidator(r'^\d{2}-\d{8}-\d{1}$', 'Ingrese un CUIT válido.')], unique=True, verbose_name= _('cuit'))
    email = CharField(max_length=50, verbose_name= _('email'), unique=True)
    address = CharField(max_length=100, verbose_name= _('address'))
    postal_code = CharField(max_length=10, verbose_name= _('postal code'))
    billing_type = CharField(max_length= 1, choices=BILLING_TYPES, default='C', verbose_name= _('billing type'))
    created_at = DateTimeField(auto_now_add=True, verbose_name= _('created at'))
    updated_at = DateTimeField(auto_now=True, verbose_name= _('updated at'))
    approved_customer_account = BooleanField(default=False, verbose_name= _('approved customer account'))
    is_deleted = BooleanField(default=False, verbose_name=_('is deleted'))
    deleted_at = DateTimeField(null=True, blank=True, verbose_name=_('deleted at'))

    def soft_delete(self):
        """
        Marks the client as deleted without removing it from the database.
        """
        self.is_deleted = True
        self.deleted_at = now()
        self.save()

    def get_full_name(self):
        return f'{self.name} {self.last_name}'

    @property
    def balance(self):
        """
        Returns the current balance of the client's account.
        If the CustomerAccount does not have any BalanceRecords, returns 0.
        """
        account_balance = self.customer_account.get_balance()
        return account_balance

    def __str__(self):
        return f'{self.name} {self.last_name}'

    class Meta:
        verbose_name = _('client')
        verbose_name_plural = _('clients')
        indexes = [
            Index(fields=['dni'], name='dni_index'),
            Index(fields=['cuit'], name='cuit_index'),
            Index(fields=['approved_customer_account'], name='approved_cc_index'),
            Index(fields=['name'], name='name_index'),
            Index(fields=['last_name'], name='last_name_index'),
            Index(fields=['phone'], name='phone_index'),
            Index(fields=['email'], name='email_index'),
        ]

    def clean(self):
        try:
            validate_email(self.email)
        except ValidationError:
            raise ValidationError({'email': _('Ingrese un email válido.')})

class CustomerBalanceRecord(Model):

    current_account = ForeignKey('CurrentAccount', on_delete=PROTECT, verbose_name=_('current account'), related_name="balance_records")
    sale = ForeignKey('sales.Sale', blank=True, null=True, on_delete=PROTECT, verbose_name=_('sale'), related_name="sale_balance_records")
    related_to = ForeignKey('self', blank=True, null=True, on_delete=SET_NULL, verbose_name=_('related to'), related_name="related_records")

    amount = DecimalField(max_digits=12, decimal_places=2, verbose_name= _('amount'))
    movement_type = CharField(max_length=20, choices=MovementType.choices, verbose_name= _('movement type'))
    notes = TextField(blank=True, null=True, verbose_name= _('notes'))
    reference = CharField(max_length=50, blank=True, null=True, verbose_name= _('reference'))
    
    created_by = ForeignKey(get_user_model(), blank=True, null=True, on_delete=SET_NULL)
    created_at = DateTimeField(auto_now_add=True, verbose_name= _('created at'), editable=False)

    reconciled = BooleanField(default=False, verbose_name= _('reconciled'))
    reconciled_at = DateTimeField(blank=True, null=True, verbose_name= _('reconciled at'))
    reconciled_by = ForeignKey(get_user_model(), blank=True, null=True, on_delete=SET_NULL, related_name='reconciled_by')

    objects: BalanceRecordsManager = BalanceRecordsManager()

    def __str__(self):
        return f'{self.current_account} - {self.amount} - {self.movement_type}'

    class Meta:
        verbose_name = _('customer balance record')
        verbose_name_plural = _('customer balance records')
        indexes = [
            Index(fields=['current_account'], name='current_account_index'),
            Index(fields=['created_at'], name='created_at_index'),
            Index(fields=['movement_type'], name='movement_type_index'),
        ]
        constraints = [
            UniqueConstraint(
                fields=['related_to', 'movement_type'],
                condition=Q(movement_type='REVERSAL'),
                name='unique_reversal_per_record'
            )
        ]
        ordering = ['-created_at']


    def validate_credit(self):
        """
        Validates that a CREDIT movement has a strictly positive amount.
        Raises:
            ValidationError: if the amount is zero or negative.
        """
        if self.amount <= 0:
            raise ValidationError({'amount': _("Credit must be positive.")})

    def validate_debit(self):
        """
        Validates that a DEBIT movement has a strictly negative amount.
        Raises:
            ValidationError: if the amount is zero or positive.
        """
        if self.amount >= 0:
            raise ValidationError({'amount': _("Debit must be negative.")})

    def validate_refund(self):
        """
        Validates that a REFUND:
        - References an existing original movement via `related_to`.

        Note: REFUNDs may be partial and multiple, so no reversal check is done.

        Raises:
            ValidationError: if `related_to` is missing.
        """
        if not self.related_to:
            raise ValidationError({NON_FIELD_ERRORS: _("Refund must reference an original record.")})

    def validate_reversal(self):
        """
        Validates that a REVERSAL:
        - References an existing original movement via `related_to`.
        - Is the only reversal for that original record.

        Raises:
            ValidationError: if `related_to` is missing or if already reversed.
        """
        if not self.related_to:
            raise ValidationError({NON_FIELD_ERRORS: _("Reversal must reference an original record.")})
        if self.related_to.related_records.filter(movement_type=MovementType.REVERSAL).exists():
            raise ValidationError({NON_FIELD_ERRORS: _("This movement has already been reversed.")})

    def validate_movement_type(self):
        """
        Calls the appropriate validation method based on the movement type.
        """
        validators = {
            MovementType.CREDIT: self.validate_credit,
            MovementType.DEBIT: self.validate_debit,
            MovementType.REVERSAL: self.validate_reversal,
            MovementType.REFUND: self.validate_refund,
        }
        validator = validators.get(self.movement_type)
        if validator:
            validator()

    def clean(self):
        """
        Performs all validations for the movement, including type, account status, and future balance.
        """
        self.validate_movement_type()

        # Validate negative balance and credit limit
        if self.current_account:
            if not self.current_account.active:
                raise ValidationError({NON_FIELD_ERRORS: _('Cannot register movements in inactive accounts.')})
            future_balance = None
            if self.pk:
                try:
                    old = CustomerBalanceRecord.objects.get(pk=self.pk)
                    future_balance = self.current_account.get_balance() - old.amount + self.amount
                except CustomerBalanceRecord.DoesNotExist:
                    future_balance = self.current_account.get_balance() + self.amount
            else:
                future_balance = self.current_account.get_balance() + self.amount
            if future_balance is not None:
                if future_balance < 0:
                    raise ValidationError({NON_FIELD_ERRORS: _('Balance cannot be negative.')})
                if self.current_account.credit_limit is not None and future_balance > self.current_account.credit_limit:
                    raise ValidationError({NON_FIELD_ERRORS: _('Balance exceeds credit limit.')})

class CustomerAccount(Model):
    client = OneToOneField(Client, on_delete=PROTECT, related_name='customer_account', verbose_name=_('client'))
    credit_limit = DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name=_('credit limit'))
    active = BooleanField(default=True, verbose_name=_('active'))
    notes = TextField(null=True, blank=True, verbose_name=_('notes'))
    opening_date = DateTimeField(auto_now_add=True, verbose_name=_('opening date'))

    def get_balance(self):
        """
        Returns the current balance of the account by summing all movements.
        """
        return self.balance_records.aggregate(balance=Sum('amount'))['balance'] or 0

    def get_movements(self, movement_type=None, start_date=None, end_date=None):
        """
        Returns movements ordered by descending date, optionally filtered by type and date range.
        """
        qs = self.balance_records.order_by('-created_at')
        if movement_type:
            qs = qs.filter(movement_type=movement_type)
        if start_date:
            qs = qs.filter(created_at__gte=start_date)
        if end_date:
            qs = qs.filter(created_at__lte=end_date)
        return qs

    def is_active(self):
        """
        Returns True if the account is active.
        """
        return self.active

    class Meta:
        verbose_name = _('current account')
        verbose_name_plural = _('current accounts')


    def deactivate(self):
        """
        Deactivates the account.
        """
        self.active = False
        self.save()
        
    def __str__(self):
        return f"{self.client.get_full_name()} - {self.opening_date}"
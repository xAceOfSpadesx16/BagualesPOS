from __future__ import annotations
from django.db.models import Model
from django.db.models.fields import CharField, DateTimeField, BooleanField, TextField, DecimalField, DateField
from django.db.models.fields.related import ForeignKey, OneToOneField
from django.db.models.deletion import SET_NULL, PROTECT
from django.db.models.aggregates import Sum
from django.db.models.constraints import UniqueConstraint
from django.db.models.query_utils import Q
from django.db.models.indexes import Index
from django.core.validators import RegexValidator, validate_email
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
from decimal import Decimal
from clients.managers import BalanceRecordsManager
from clients.choices import MovementType, BillingType

from utils import PhoneNumberField

class Client(Model):

    name = CharField(_('name'),max_length=50)
    last_name = CharField(_('last_name'), max_length=50)
    phone = PhoneNumberField(null=True, blank=True, verbose_name= _('phone number'))
    dni = CharField(max_length=9, verbose_name= _('dni'))
    cuit = CharField(max_length=13, null=True, validators=[RegexValidator(r'^\d{2}-\d{8}-\d{1}$', 'Ingrese un CUIT válido.')], unique=True, verbose_name= _('cuit'))
    email = CharField(max_length=50, verbose_name= _('email'), unique=True)
    address = CharField(max_length=100, verbose_name= _('address'))
    birth_date = DateField(null=True, blank=True, verbose_name= _('birth date'))
    postal_code = CharField(max_length=10, verbose_name= _('postal code'))
    chosen_billing_type = CharField(max_length= 2, choices=BillingType.choices, default='C', verbose_name= _('billing type'))
    created_at = DateTimeField(auto_now_add=True, verbose_name= _('created at'))
    updated_at = DateTimeField(auto_now=True, verbose_name= _('updated at'))
    approved_customer_account = BooleanField(default=True, verbose_name= _('approved customer account'))
    is_deleted = BooleanField(default=False, verbose_name=_('is deleted'))
    deleted_at = DateTimeField(null=True, blank=True, verbose_name=_('deleted at'))

    def soft_delete(self):
        """
        Marks the client as deleted without removing it from the database.
        """
        self.is_deleted = True
        self.deleted_at = now()
        self.save()

    def restore(self):
        """
        Restores a soft-deleted client.
        """
        self.is_deleted = False
        self.deleted_at = None
        self.save()

    @property
    def get_full_name(self):
        return f'{self.name} {self.last_name}'

    @property
    def balance(self):
        return self.customer_account.balance if hasattr(self, 'customer_account') else Decimal('0.00')

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


class CustomerAccount(Model):
    client = OneToOneField(Client, on_delete=PROTECT, related_name='customer_account', verbose_name=_('client'))
    credit_limit = DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name=_('credit limit'))
    active = BooleanField(default=True, verbose_name=_('active'))
    notes = TextField(null=True, blank=True, verbose_name=_('notes'))
    opening_date = DateTimeField(auto_now_add=True, verbose_name=_('opening date'))

    @property
    def is_active(self):
        return self.active

    @property
    def balance(self):
        return self.balance_records.effective().client_balance()

    @property
    def get_balance(self):
        return self.balance

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


    class Meta:
        verbose_name = _('customer account')
        verbose_name_plural = _('customer accounts')


    def deactivate(self):
        """
        Deactivates the account.
        """
        self.active = False
        self.save()
        
    def __str__(self):
        return f"{_('Customer Account')} N° {self.id} {self.client.get_full_name}"


class CustomerBalanceRecord(Model):

    customer_account = ForeignKey(CustomerAccount, on_delete=PROTECT, verbose_name=_('customer account'), related_name="balance_records")
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
        return f'{self.customer_account} - ${self.amount} - {self.movement_type} - {self.created_at.strftime("%d/%m/%Y %H:%M:%S")}'

    class Meta:
        verbose_name = _('customer balance record')
        verbose_name_plural = _('customer balance records')
        indexes = [
            Index(fields=['customer_account'], name='customer_account_index'),
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


    def _validate_same_account(self):
        if self.related_to and self.related_to.customer_account_id != self.customer_account_id:
            raise ValidationError({'related_to': _("The related movement must belong to the same customer account.")})


    def validate_credit(self):
        """
        Validates that a CREDIT movement has a strictly positive amount.
        Raises:
            ValidationError: if the amount is zero or negative.
        """
        if self.amount <= 0:
            raise ValidationError({'amount': _("Credit must be greater than zero.")})

    def validate_debit(self):
        """
        Validates that a DEBIT movement has a strictly positive amount.
        Raises:
            ValidationError: if the amount is zero or negative.
        """
        if self.amount <= 0:
            raise ValidationError({'amount': _("Debit must be greater than zero.")})

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
        self._validate_same_account()

    def validate_reversal(self):
        """
        Validates that a REVERSAL:
        - References an existing original movement via `related_to`.
        - Is the only reversal for that original record.

        Raises:
            ValidationError: if `related_to` is missing or if already reversed.
        """
        if not self.related_to:
            raise ValidationError({"related_to": _("Reversal must reference an original record.")})
        self._validate_same_account()
        if self.related_to.related_records.filter(movement_type=MovementType.REVERSAL).exists():
            raise ValidationError({"related_to": _("This movement has already been reversed.")})

    def validate_adjustment(self):
        if not self.related_to:
            raise ValidationError({"related_to": _("Adjustment must reference an original record.")})
        self._validate_same_account()

    def validate_movement_type(self):
        validators = {
            MovementType.CREDIT: self.validate_credit,
            MovementType.DEBIT: self.validate_debit,
            MovementType.REVERSAL: self.validate_reversal,
            MovementType.REFUND: self.validate_refund,
            MovementType.ADJUSTMENT: self.validate_adjustment,  # ← nuevo
        }
        validator = validators.get(self.movement_type)
        if validator:
            validator()


    def _delta_client_balance(self) -> Decimal:
        """
        Variación firmada del saldo cliente según el tipo:
        + = a favor / - = debe
        """
        if self.movement_type == MovementType.DEBIT:
            return Decimal(self.amount) * Decimal('-1')
        if self.movement_type in (MovementType.CREDIT, MovementType.REFUND):
            return Decimal(self.amount)
        if self.movement_type == MovementType.ADJUSTMENT:
            if self.related_to:
                if self.related_to.movement_type == MovementType.DEBIT:
                    return Decimal(self.amount)      # corrige un DEBIT → suma (a favor)
                if self.related_to.movement_type == MovementType.CREDIT:
                    return Decimal(self.amount) * Decimal('-1')  # corrige un CREDIT → resta
        return Decimal('0.00')



    def clean(self):
        """
        Validaciones por tipo + estado de cuenta + límite de crédito.
        """
        self.validate_movement_type()

        if self.customer_account:
            if not self.customer_account.active:
                raise ValidationError({NON_FIELD_ERRORS: _('Cannot register movements in inactive accounts.')})

            # Balance actual
            current = self.customer_account.balance

            # Impacto del nuevo movimiento
            new_delta = self._delta_client_balance()

            # Si edito, saco el impacto anterior y sumo el nuevo
            if self.pk:
                try:
                    old = CustomerBalanceRecord.objects.get(pk=self.pk)
                    current -= old._delta_client_balance()
                except CustomerBalanceRecord.DoesNotExist:
                    pass

            future_balance = current + new_delta

            # Límite de crédito: no permitir deber más que credit_limit
            if self.customer_account.credit_limit is not None:
                max_debt = Decimal(self.customer_account.credit_limit) * Decimal('-1')
                if future_balance < max_debt:
                    raise ValidationError({NON_FIELD_ERRORS: _('Balance exceeds credit limit.')})
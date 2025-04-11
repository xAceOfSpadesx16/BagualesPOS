from django.db.models import Model
from django.db.models.fields import CharField, DateTimeField, BooleanField, IntegerField
from django.db.models.fields.related import ForeignKey
from django.db.models.deletion import CASCADE
from django.core.validators import RegexValidator
from utils import PhoneNumberField
from django.utils.translation import gettext_lazy as _

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
    email = CharField(max_length=50, verbose_name= _('email'))
    address = CharField(max_length=100, verbose_name= _('address'))
    city = CharField(max_length=50, verbose_name= _('city'))
    postal_code = CharField(max_length=10, verbose_name= _('postal code'))
    country = CharField(max_length=50, verbose_name= _('country'))
    billing_type = CharField(max_length= 1, choices=BILLING_TYPES, default='C', verbose_name= _('billing type'))
    balance = IntegerField(default=0, verbose_name= _('balance'))
    created_at = DateTimeField(auto_now_add=True, verbose_name= _('created at'))
    updated_at = DateTimeField(auto_now=True, verbose_name= _('updated at'))
    approved_customer_account = BooleanField(default=False, verbose_name= _('approved customer account'))

    def get_full_name(self):
        return f'{self.name} {self.last_name}'

    def __str__(self):
        return f'{self.name} {self.last_name}'

    class Meta:
        verbose_name = _('client')
        verbose_name_plural = _('clients')

class CustomerBalanceRecord(Model):
    client = ForeignKey(Client, on_delete=CASCADE, verbose_name= _('client'))
    amount = IntegerField(verbose_name= _('amount'))
    created_at = DateTimeField(auto_now_add=True, verbose_name= _('created at'), editable=False)

    def __str__(self):
        return f'{self.client.name} {self.client.last_name} - {self.amount}'

    class Meta:
        verbose_name = _('customer balance record')
        verbose_name_plural = _('customer balance records')



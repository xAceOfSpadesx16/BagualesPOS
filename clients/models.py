from django.db.models import Model
from django.db.models.fields import CharField, DateTimeField, BooleanField, IntegerField
from django.db.models.fields.related import ForeignKey
from django.db.models.deletion import CASCADE
from django.core.validators import RegexValidator
from utils import PhoneNumberField

class Client(Model):

    BILLING_TYPES = (
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('E', 'E'),
        ('M', 'M'),
        ('T', 'T'),
    )

    name = CharField(max_length=50)
    last_name = CharField(max_length=50)
    phone = PhoneNumberField()
    dni = CharField(max_length=9)
    cuit = CharField(max_length=11, null=True, validators=[RegexValidator(r'^\d{2}-\d{8}-\d{1}$', 'Ingrese un CUIT válido.')], unique=True)
    email = CharField(max_length=50)
    address = CharField(max_length=100)
    city = CharField(max_length=50)
    postal_code = CharField(max_length=10)
    country = CharField(max_length=50)
    billing_type = CharField(max_length= 1, choices=BILLING_TYPES, default='C')
    balance = IntegerField(default=0)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    approved_customer_account = BooleanField(default=False)

    def get_full_name(self):
        return f'{self.name} {self.last_name}'

    def __str__(self):
        return f'{self.name} {self.last_name}'

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

class CustomerBalanceRecord(Model):
    client = ForeignKey(Client, on_delete=CASCADE)
    amount = IntegerField()
    created_at = DateTimeField(auto_now_add=True)


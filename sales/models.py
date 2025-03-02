from django.db.models import Model
from django.db.models.fields import DateTimeField, DecimalField, BooleanField, CharField
from django.db.models.fields.related import ForeignKey
from django.db.models.deletion import CASCADE, SET_NULL
from decimal import Decimal, ROUND_HALF_UP
from django.contrib.auth import get_user_model

from sales.managers import SalesManager
from products.models import Product
from clients.models import Client

class PayMethod(Model):
    name = CharField(max_length=50)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Método de Pago'
        verbose_name_plural = 'Métodos de Pago'

    def __str__(self):
        return self.name

class Sale(Model):
    seller = ForeignKey(get_user_model(), on_delete=SET_NULL, null=True)
    client = ForeignKey(Client, on_delete=SET_NULL, null=True)
    total_amount = DecimalField(max_digits=10, decimal_places=2, default=0)
    pay_method = ForeignKey(PayMethod, on_delete=SET_NULL, null=True)
    canceled = BooleanField(default=False)
    closed = BooleanField(default=False)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    objects: SalesManager = SalesManager()


    class Meta:
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'

    def __str__(self):
        return f'Venta {self.pk} - {self.seller.get_full_name()} - {self.created_at} {f"- {self.client.name}" if self.client else ""}'

class SaleDetail(Model):
    order = ForeignKey(Sale, on_delete=CASCADE, related_name='details')
    product = ForeignKey(Product, on_delete= SET_NULL, null=True)
    quantity = DecimalField(max_digits=10, decimal_places=2)
    sale_price = DecimalField(max_digits=10, decimal_places=2)
    created_at = DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Detalle de Venta'
        verbose_name_plural = 'Detalles de Ventas'

    def __str__(self):
        return f'{self.product} - {self.quantity} - {self.sale_price}'
    
    def get_total_price(self):
        return (self.quantity * self.sale_price).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    
    def save(self, *args, **kwargs):
        self.order.total_amount += self.get_total_price()
        self.order.save()
        super().save(*args, **kwargs)
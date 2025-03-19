from django.db.models import Model
from django.db.models.fields import DateTimeField, BooleanField, CharField, IntegerField
from django.db.models.fields.related import ForeignKey
from django.db.models.deletion import CASCADE, SET_NULL
from django.contrib.auth import get_user_model

from sales.managers import SalesManager
from products.models import Product
from clients.models import Client

from utils.formats import formatted_integer

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
    total_amount = IntegerField(default=0)
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
    
    @property
    def formatted_total_amount(self):
        return formatted_integer(self.total_amount)
    

class SaleDetail(Model):
    order = ForeignKey(Sale, on_delete=CASCADE, related_name='details')
    product = ForeignKey(Product, on_delete= SET_NULL, null=True)
    quantity = IntegerField(default=1, help_text='Cantidad')
    sale_price = IntegerField()
    created_at = DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Detalle de Venta'
        verbose_name_plural = 'Detalles de Ventas'

    def __str__(self):
        return f'{self.product} - {self.quantity} - {self.sale_price}'
    
    @property
    def get_total_price(self):
        return self.quantity * self.sale_price
    
    @property
    def formatted_total_price(self):
        return formatted_integer(self.get_total_price)
    
    @property
    def formatted_sale_price(self):
        return formatted_integer(self.sale_price)

    
    def save(self, *args, **kwargs):
        self.sale_price = self.product.sale_price
        super().save(*args, **kwargs)

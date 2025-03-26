from django.db.models import Model
from django.db.models.fields import DateTimeField, BooleanField, CharField, IntegerField
from django.db.models.fields.related import ForeignKey
from django.db.models.deletion import CASCADE, SET_NULL
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from sales.managers import SalesManager
from products.models import Product
from clients.models import Client

from utils.formats import formatted_integer

class PayMethod(Model):
    name = CharField(max_length=50, verbose_name= _('name'))
    created_at = DateTimeField(auto_now_add=True, editable= False, verbose_name= _('created at'))
    updated_at = DateTimeField(auto_now=True, verbose_name= _('updated at'))

    class Meta:
        verbose_name = _('payment method')
        verbose_name_plural = _('payment methods')

    def __str__(self):
        return self.name

class Sale(Model):
    seller = ForeignKey(get_user_model(), on_delete=SET_NULL, null=True, verbose_name= _('seller'))
    client = ForeignKey(Client, on_delete=SET_NULL, null=True, verbose_name= _('client'))
    total_amount = IntegerField(default=0, verbose_name= _('total amount'))
    pay_method = ForeignKey(PayMethod, on_delete=SET_NULL, null=True, verbose_name= _('payment method'))
    canceled = BooleanField(default=False, verbose_name= _('canceled'))
    closed = BooleanField(default=False, verbose_name= _('closed'))
    created_at = DateTimeField(auto_now_add=True, verbose_name= _('created at'))
    updated_at = DateTimeField(auto_now=True, verbose_name= _('updated at'))

    objects: SalesManager = SalesManager()


    class Meta:
        verbose_name = _('sale')
        verbose_name_plural = _('sales')

    def __str__(self):
        return f'{_('sale')} {self.pk} - {self.seller.get_full_name()} - {self.created_at} {f"- {self.client.name}" if self.client else ""}'
    
    @property
    def formatted_total_amount(self):
        return formatted_integer(self.total_amount)
    

class SaleDetail(Model):
    order = ForeignKey(Sale, on_delete=CASCADE, related_name='details', verbose_name= _('order'))
    product = ForeignKey(Product, on_delete= SET_NULL, null=True, verbose_name= _('product'))
    quantity = IntegerField(default=1, help_text='Cantidad', verbose_name= _('quantity'))
    sale_price = IntegerField(verbose_name= _('sale price'))
    created_at = DateTimeField(auto_now_add=True, verbose_name= _('created at'))

    class Meta:
        verbose_name = _('sale detail')
        verbose_name_plural = _('sale details')

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

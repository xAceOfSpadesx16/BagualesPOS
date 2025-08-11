from django.forms.fields import BooleanField
from products.forms import AdministrationForm
from django.utils.translation import gettext_lazy as _
from django import forms
from .models import CustomerBalanceRecord, CurrentAccount


class ClientForm(AdministrationForm):

    class Meta:
        fields=["name", "last_name", "phone", "dni", "cuit", "email", "address", "postal_code", "billing_type", "approved_customer_account"]
        widgets={
            "approved_customer_account": BooleanField(label=_("Approved customer account"))
        }


class CustomerBalanceRecordForm(forms.ModelForm):
    class Meta:
        model = CustomerBalanceRecord
        fields = ['current_account', 'amount', 'movement_type', 'notes', 'reference', 'related_to', 'sale']


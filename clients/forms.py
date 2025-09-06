from django.forms.fields import BooleanField
from products.forms import AdministrationForm
from django.utils.translation import gettext_lazy as _
from django import forms
from clients.models import CustomerBalanceRecord, Client, CustomerAccount

class ClientForm(AdministrationForm):

    class Meta:
        model = Client
        fields=[
            "name", 
            "last_name", 
            "phone", 
            "dni", 
            "cuit", 
            "email", 
            "address", 
            "postal_code", 
            "chosen_billing_type", 
            "approved_customer_account"
        ]
        widgets={
            # "approved_customer_account": forms.CheckboxInput(attrs={'label': _("Approved customer account")}),
            "postal_code": forms.TextInput(attrs={'placeholder': _('Postal Code')}),
            "chosen_billing_type": forms.Select(attrs={'class': 'form-select', "placeholder": _('Chosen Billing Type')}),
        }


class CustomerBalanceRecordForm(AdministrationForm):
    class Meta:
        model = CustomerBalanceRecord
        fields = [
            'customer_account',
            'sale',
            'amount',
            'movement_type',
            'notes',
            'reference',
            'related_to',
        ]


class CustomerAccountForm(AdministrationForm):
    class Meta:
        model = CustomerAccount
        fields = [
            'credit_limit',
            'notes',
        ]
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': _('Notes')}),
        }

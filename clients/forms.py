from django.forms.fields import BooleanField
from products.forms import AdministrationForm
from django.utils.translation import gettext_lazy as _
from django import forms
from django.core.exceptions import ImproperlyConfigured
from clients.models import CustomerBalanceRecord, Client, CustomerAccount
from clients.choices import MovementType

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
            "postal_code": forms.TextInput(attrs={'placeholder': _('Postal Code')}),
            "chosen_billing_type": forms.Select(attrs={'class': 'form-select', "placeholder": _('Chosen Billing Type')}),
        }


class BalanceRecordForm(AdministrationForm):

    def __init__(self, *args, customer_account=None, created_by=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Asegurar instancia con cuenta
        self.instance.customer_account = customer_account or self.instance.customer_account
        if self.instance.customer_account is None and self.instance.pk is None:
            raise ImproperlyConfigured(_("A CustomerAccount must be provided to create a new BalanceRecord."))

        self._created_by = created_by

        # related_to: solo movimientos de la misma cuenta (UX)
        qs = CustomerBalanceRecord.objects.filter(
            customer_account=self.instance.customer_account
        ).exclude(pk=self.instance.pk).exclude(movement_type=MovementType.REVERSAL)
        self.fields['related_to'].queryset = qs.order_by('-created_at')

        if 'sale' in self.fields and hasattr(self.instance.customer_account, 'client_id'):
            Sale = self.fields['sale'].queryset.model
            if hasattr(Sale, 'client_id'):
                self.fields['sale'].queryset = self.fields['sale'].queryset.filter(
                    client_id=self.instance.customer_account.client_id
                ).order_by('-created_at')

    class Meta:
        model = CustomerBalanceRecord
        fields = [
            'movement_type',
            'amount',
            'sale',
            'notes',
            'reference',
            'related_to',
        ]

    def clean(self):
        datos = super().clean()
        movimiento_relacionado = datos.get('related_to')
        if movimiento_relacionado and movimiento_relacionado.customer_account_id != self.instance.customer_account_id:
            raise forms.ValidationError(_("The related movement must belong to the same customer account."))
        return datos


    def save(self, commit=True):
        self.instance.created_by = self._created_by
        return super().save(commit)


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

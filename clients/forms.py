from django.forms.fields import BooleanField
from products.forms import AdministrationForm
from django.utils.translation import gettext_lazy as _


class ClientForm(AdministrationForm):


    class Meta:
        fields=["name", "last_name", "phone", "dni", "cuit", "email", "address", "postal_code", "billing_type", "approved_customer_account"]
        widgets={
            "approved_customer_account": BooleanField(label=_("Approved customer account"))
        }


from dal import autocomplete
from django import forms
from django.forms import ModelForm
from django.forms.fields import IntegerField
from sales.models import SaleDetail, Sale
from products.models import Product


class SearchProductForm(ModelForm):
    quantity = IntegerField(required=True, initial= 1, min_value=1, help_text= "Cantidad")

    class Meta:
        model = SaleDetail
        fields = ("product", 'quantity')
        widgets = {
            "product": autocomplete.ModelSelect2(
                url="product-autocomplete",
                attrs={
                    "data-placeholder": "Buscar un producto",
                },
            ),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)
        self.fields["submit"] = forms.CharField(
            widget=forms.HiddenInput(), required=False
        )

    def save(self, *args, **kwargs):
        # Get the sale
        sale = Sale.objects.get_table_active_sale(self.request.user)
        if not sale:
            sale = Sale.objects.create(seller=self.request.user)
        self.instance.sale = sale  # Assign sale to instance of SaleDetail
        
        # check if exist product
        if SaleDetail.objects.filter(product=self.cleaned_data.get("product"), sale=sale).exists():
            raise forms.ValidationError("El producto ya existe en la venta.")
        
        # save the instance
        return super().save(*args, **kwargs)
        

    def clean_product(self):
        product = self.cleaned_data.get("product")
        if not product:
            raise forms.ValidationError("El campo producto es obligatorio")
        return product

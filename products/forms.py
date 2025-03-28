from django.forms import ModelForm, CharField, Textarea, FileInput

from products.models import Product

class ProductForm(ModelForm):

    details = CharField(widget= Textarea())

    class Meta:
        model = Product
        fields = [
            'name',
            'brand',
            'material',
            'numeric_size',
            'letter_size',
            'cost_price',
            'sale_price',
            'gender',
            'details',
            'color',
            'category',
            'season',
            'image'
        ]
        widgets = {
            'image': FileInput(attrs={
                'class': 'custom-file-input',
            }),
        }
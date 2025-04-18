from django.forms import ModelForm, CharField, Textarea, FileInput

from products.models import Product, Brand, Category, Color, Gender, LetterSize, Materials, Season, Supplier


class ProductForm(ModelForm):

    details = CharField(widget= Textarea(), required=False)

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

class BrandForm(ModelForm):
    class Meta:
        model = Brand
        fields = ['name', 'supplier', 'logo']

class CategoryForm(ModelForm):
    class Meta:
        model = Category
        fields = ['name']

class ColorForm(ModelForm):
    class Meta:
        model = Color
        fields = ['name', 'code']

class GenderForm(ModelForm):
    class Meta:
        model = Gender
        fields = ['name']

class LetterSizeForm(ModelForm):
    class Meta:
        model = LetterSize
        fields = ['name']

class MaterialsForm(ModelForm):
    class Meta:
        model = Materials
        fields = ['name']

class SeasonForm(ModelForm):
    class Meta:
        model = Season
        fields = ['name']

class SupplierForm(ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'phone_number', 'email']
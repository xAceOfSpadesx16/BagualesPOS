from django.forms import ModelForm, CharField, Textarea, FileInput, TextInput
from django.forms.boundfield import BoundField

from products.models import Product, Brand, Category, Color, Gender, LetterSize, Materials, Season, Supplier

from utils.mixins import FormGroupMixin, RequiredSuffixMixin


class AdministrationForm(FormGroupMixin, RequiredSuffixMixin, ModelForm): ...


class ProductForm(RequiredSuffixMixin, ModelForm):

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


class BrandForm(AdministrationForm):
    class Meta:
        model = Brand
        fields = ['name', 'supplier', 'logo']


class CategoryForm(AdministrationForm):
    class Meta:
        model = Category
        fields = ['name']



# class ColorForm(AdministrationForm):
class ColorForm(AdministrationForm):
    class Meta:
        model = Color
        fields = ['name', 'code']
        widgets = {
            'code': TextInput(attrs={'type': 'color'})
        }

class GenderForm(AdministrationForm):
    class Meta:
        model = Gender
        fields = ['name']

class LetterSizeForm(AdministrationForm):
    class Meta:
        model = LetterSize
        fields = ['name']

class MaterialsForm(AdministrationForm):
    class Meta:
        model = Materials
        fields = ['name']

class SeasonForm(AdministrationForm):
    class Meta:
        model = Season
        fields = ['name']

class SupplierForm(AdministrationForm):
    class Meta:
        model = Supplier
        fields = ['name', 'phone_number', 'email']
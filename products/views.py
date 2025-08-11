from django.views.generic.base import View
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _


from products.models import Product, Brand, Category, Color, Gender, LetterSize, Materials, Season, Supplier

from products.forms import ProductForm, BrandForm, CategoryForm, ColorForm, GenderForm, LetterSizeForm, MaterialsForm, SeasonForm, SupplierForm

from utils.mixins import CreateFormValidationMixin, UpdateFormValidationMixin

    
""" PRODUCT VIEWS """

class ProductListView(ListView):
    template_name = 'product_administration.html'
    model = Product
    context_object_name = 'products'
    queryset = Product.objects.filter(is_deleted=False)


class ProductCreateView(CreateFormValidationMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'product_form.html'
    success_url = reverse_lazy('administration')


class ProductUpdateView(UpdateFormValidationMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'product_form.html'
    success_url = reverse_lazy('administration')


class ProductDeleteView(View):
    http_method_names = ['delete']

    def delete(self, request: HttpRequest, pk, *args, **kwargs):
        product = get_object_or_404(Product, id=pk)
        product.soft_delete()
        return JsonResponse({"message": f"{_('Product deleted successfully')}: {product.name} - {product.brand.name}"}, status=200)


""" BRAND VIEWS """

class BrandListView(ListView):
    template_name = 'brand_administration.html'
    model = Brand
    context_object_name = 'brands'
    

class BrandCreateView(CreateFormValidationMixin, CreateView):
    model = Brand
    form_class = BrandForm
    template_name = 'administration_forms.html'
    success_url = reverse_lazy('brand_administration')

    
class BrandUpdateView(UpdateFormValidationMixin, UpdateView):
    model = Brand
    form_class = BrandForm
    template_name = 'administration_forms.html'
    success_url = reverse_lazy('brand_administration')


class BrandDeleteView(View):
    http_method_names = ['delete']

    def delete(self, request: HttpRequest, pk, *args, **kwargs):
        brand = get_object_or_404(Brand, id=pk)
        brand.delete()
        return JsonResponse({"message": f"{_('Brand deleted successfully')}: {brand.name}')"}, status=200)


""" CATEGORY VIEWS """

class CategoryListView(ListView):
    template_name = 'category_administration.html'
    model = Category
    context_object_name = 'categories'

class CategoryCreateView(CreateFormValidationMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'administration_forms.html'
    success_url = reverse_lazy('category_administration')

class CategoryUpdateView(UpdateFormValidationMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'administration_forms.html'
    success_url = reverse_lazy('category_administration')

class CategoryDeleteView(View):
    http_method_names = ['delete']

    def delete(self, request: HttpRequest, pk, *args, **kwargs):
        category = get_object_or_404(Category, id=pk)
        category.delete()
        return JsonResponse({"message": f"{_('Category deleted successfully')}: {category.name}"}, status=200)


""" COLOR VIEWS """

class ColorListView(ListView):
    template_name = 'color_administration.html'
    model = Color
    context_object_name = 'colors'

class ColorCreateView(CreateFormValidationMixin, CreateView):
    model = Color
    form_class = ColorForm
    template_name = 'administration_forms.html'
    success_url = reverse_lazy('color_administration')


class ColorUpdateView(UpdateFormValidationMixin, UpdateView):
    model = Color
    form_class = ColorForm
    template_name = 'administration_forms.html'
    success_url = reverse_lazy('color_administration')

class ColorDeleteView(View):
    http_method_names = ['delete']

    def delete(self, request: HttpRequest, pk, *args, **kwargs):
        color = get_object_or_404(Color, id=pk)
        color.delete()
        return JsonResponse({"message": f"{_('Color deleted successfully')}: {color.name}"}, status=200)


""" Gender VIEWS """

class GenderListView(ListView):
    template_name = 'gender_administration.html'
    model = Gender
    context_object_name = 'genders'

class GenderCreateView(CreateFormValidationMixin, CreateView):
    model = Gender
    form_class = GenderForm
    template_name = 'administration_forms.html'
    success_url = reverse_lazy('gender_administration')

class GenderUpdateView(UpdateFormValidationMixin, UpdateView):
    model = Gender
    form_class = GenderForm
    template_name = 'administration_forms.html'
    success_url = reverse_lazy('gender_administration')

class GenderDeleteView(View):
    http_method_names = ['delete']

    def delete(self, request: HttpRequest, pk, *args, **kwargs):
        gender = get_object_or_404(Gender, id=pk)
        gender.delete()
        return JsonResponse({"message": f"{_('Gender deleted successfully')}: {gender.name}"}, status=200)


""" LetterSize VIEWS """

class LetterSizeListView(ListView):
    template_name = 'letter_size_administration.html'
    model = LetterSize
    context_object_name = 'letter_sizes'

class LetterSizeCreateView(CreateFormValidationMixin, CreateView):
    model = LetterSize
    form_class = LetterSizeForm
    template_name = 'administration_forms.html'
    success_url = reverse_lazy('letter_size_administration')

class LetterSizeUpdateView(UpdateFormValidationMixin, UpdateView):
    model = LetterSize
    form_class = LetterSizeForm
    template_name = 'administration_forms.html'
    success_url = reverse_lazy('letter_size_administration')

class LetterSizeDeleteView(View):
    http_method_names = ['delete']

    def delete(self, request: HttpRequest, pk, *args, **kwargs):
        letter_size = get_object_or_404(LetterSize, id=pk)
        letter_size.delete()
        return JsonResponse({"message": f"{_('Letter size deleted successfully')}: {letter_size.name}"}, status=200)


""" Materials VIEWS """

class MaterialsListView(ListView):
    template_name = 'material_administration.html'
    model = Materials
    context_object_name = 'materials'

class MaterialsCreateView(CreateFormValidationMixin, CreateView):
    model = Materials
    form_class = MaterialsForm
    template_name = 'administration_forms.html'
    success_url = reverse_lazy('materials_administration')

class MaterialsUpdateView(UpdateFormValidationMixin, UpdateView):
    model = Materials
    form_class = MaterialsForm
    template_name = 'administration_forms.html'
    success_url = reverse_lazy('materials_administration')

class MaterialsDeleteView(View):
    http_method_names = ['delete']

    def delete(self, request: HttpRequest, pk, *args, **kwargs):
        material = get_object_or_404(Materials, id=pk)
        material.delete()
        return JsonResponse({"message": f"{_('Material deleted successfully')}: {material.name}"}, status=200)


""" Season VIEWS """

class SeasonListView(ListView):
    template_name = 'season_administration.html'
    model = Season
    context_object_name = 'seasons'

class SeasonCreateView(CreateFormValidationMixin, CreateView):
    model = Season
    form_class = SeasonForm
    template_name = 'administration_forms.html'
    success_url = reverse_lazy('season_administration')

class SeasonUpdateView(UpdateFormValidationMixin, UpdateView):
    model = Season
    form_class = SeasonForm
    template_name = 'administration_forms.html'
    success_url = reverse_lazy('season_administration')

class SeasonDeleteView(View):
    http_method_names = ['delete']

    def delete(self, request: HttpRequest, pk, *args, **kwargs):
        season = get_object_or_404(Season, id=pk)
        season.delete()
        return JsonResponse({"message": f"{_('Season deleted successfully')}: {season.name}"}, status=200)


""" Supplier VIEWS """

class SupplierListView(ListView):
    template_name = 'supplier_administration.html'
    model = Supplier
    context_object_name = 'suppliers'

class SupplierCreateView(CreateFormValidationMixin, CreateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'administration_forms.html'
    success_url = reverse_lazy('supplier_administration')

class SupplierUpdateView(UpdateFormValidationMixin, UpdateView):    
    model = Supplier
    form_class = SupplierForm
    template_name = 'administration_forms.html'
    success_url = reverse_lazy('supplier_administration')

class SupplierDeleteView(View):
    http_method_names = ['delete']

    def delete(self, request: HttpRequest, pk, *args, **kwargs):
        supplier = get_object_or_404(Supplier, id=pk)
        supplier.delete()
        return JsonResponse({"message": f"{_('Supplier deleted successfully')}: {supplier.name}"}, status=200)
    

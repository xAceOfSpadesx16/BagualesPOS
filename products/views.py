from django.views.generic.base import View
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from django.urls import reverse_lazy
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _


from products.models import Product, Brand, Category, Color, Gender, LetterSize, Materials, Season, Supplier

from products.forms import ProductForm, BrandForm, CategoryForm, ColorForm, GenderForm, LetterSizeForm, MaterialsForm, SeasonForm, SupplierForm

from utils.mixins import FormValidationMixin, FetchRequestMixin

    
""" PRODUCT VIEWS """

class ProductListView(ListView):
    template_name = 'product_administration.html'
    model = Product
    context_object_name = 'products'
    queryset = Product.objects.filter(is_deleted=False)


class ProductCreateView(FormValidationMixin, FetchRequestMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'product_form.html'
    success_url = reverse_lazy('administration')

class ProductUpdateView(FormValidationMixin, FetchRequestMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'product_form.html'
    success_url = reverse_lazy('administration')


class ProductDeleteView(FetchRequestMixin, View):
    http_method_names = ['delete']
    success_url = reverse_lazy('product_administration')

    def delete(self, request: HttpRequest, pk, *args, **kwargs):
        product = get_object_or_404(Product, id=pk)
        product.soft_delete()
        return HttpResponseRedirect(self.success_url)


""" BRAND VIEWS """

class BrandListView(ListView):
    template_name = 'brand_administration.html'
    model = Brand
    context_object_name = 'brands'
    

class BrandCreateView(FormValidationMixin, FetchRequestMixin, CreateView):
    model = Brand
    form_class = BrandForm
    template_name = 'administration_forms.html'
    success_url = reverse_lazy('brand_administration')


class BrandUpdateView(FormValidationMixin, FetchRequestMixin, UpdateView):
    model = Brand
    form_class = BrandForm
    template_name = 'administration_forms.html'
    success_url = reverse_lazy('brand_administration')


class BrandDeleteView(FetchRequestMixin, View):
    http_method_names = ['delete']
    success_url = reverse_lazy('brand_administration')

    def delete(self, request: HttpRequest, pk, *args, **kwargs):
        brand = get_object_or_404(Brand, id=pk)
        brand.delete()
        return HttpResponseRedirect(self.success_url)


""" CATEGORY VIEWS """

class CategoryListView(ListView):
    template_name = 'category_administration.html'
    model = Category
    context_object_name = 'categories'

class CategoryCreateView(FormValidationMixin, FetchRequestMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'administration_forms.html'
    success_url = reverse_lazy('category_administration')

class CategoryUpdateView(FormValidationMixin, FetchRequestMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'administration_forms.html'
    success_url = reverse_lazy('category_administration')

class CategoryDeleteView(FetchRequestMixin, View):
    http_method_names = ['delete']
    success_url = reverse_lazy('category_administration')

    def delete(self, request: HttpRequest, pk, *args, **kwargs):
        category = get_object_or_404(Category, id=pk)
        category.delete()
        return HttpResponseRedirect(self.success_url)

""" COLOR VIEWS """

class ColorListView(ListView):
    template_name = 'color_administration.html'
    model = Color
    context_object_name = 'colors'

class ColorCreateView(FormValidationMixin, FetchRequestMixin, CreateView):
    model = Color
    form_class = ColorForm
    template_name = 'administration_forms.html'
    success_url = reverse_lazy('color_administration')


class ColorUpdateView(FormValidationMixin, FetchRequestMixin, UpdateView):
    model = Color
    form_class = ColorForm
    template_name = 'administration_forms.html'
    success_url = reverse_lazy('color_administration')

class ColorDeleteView(FetchRequestMixin, View):
    http_method_names = ['delete']
    success_url = reverse_lazy('color_administration')

    def delete(self, request: HttpRequest, pk, *args, **kwargs):
        color = get_object_or_404(Color, id=pk)
        color.delete()
        return HttpResponseRedirect(self.success_url)

""" Gender VIEWS """

class GenderListView(ListView):
    template_name = 'gender_administration.html'
    model = Gender
    context_object_name = 'genders'

class GenderCreateView(FormValidationMixin, FetchRequestMixin, CreateView):
    model = Gender
    form_class = GenderForm
    template_name = 'administration_forms.html'
    success_url = reverse_lazy('gender_administration')

class GenderUpdateView(FormValidationMixin, FetchRequestMixin, UpdateView):
    model = Gender
    form_class = GenderForm
    template_name = 'administration_forms.html'
    success_url = reverse_lazy('gender_administration')

class GenderDeleteView(FetchRequestMixin, View):
    http_method_names = ['delete']
    success_url = reverse_lazy('gender_administration')

    def delete(self, request: HttpRequest, pk, *args, **kwargs):
        gender = get_object_or_404(Gender, id=pk)
        gender.delete()
        return HttpResponseRedirect(self.success_url)


""" LetterSize VIEWS """

class LetterSizeListView(ListView):
    template_name = 'letter_size_administration.html'
    model = LetterSize
    context_object_name = 'letter_sizes'

class LetterSizeCreateView(FormValidationMixin, FetchRequestMixin, CreateView):
    model = LetterSize
    form_class = LetterSizeForm
    template_name = 'administration_forms.html'
    success_url = reverse_lazy('letter_size_administration')

class LetterSizeUpdateView(FormValidationMixin, FetchRequestMixin, UpdateView):
    model = LetterSize
    form_class = LetterSizeForm
    template_name = 'administration_forms.html'
    success_url = reverse_lazy('letter_size_administration')

class LetterSizeDeleteView(FetchRequestMixin, View):
    http_method_names = ['delete']
    success_url = reverse_lazy('letter_size_administration')

    def delete(self, request: HttpRequest, pk, *args, **kwargs):
        letter_size = get_object_or_404(LetterSize, id=pk)
        letter_size.delete()
        return HttpResponseRedirect(self.success_url)


""" Materials VIEWS """

class MaterialsListView(ListView):
    template_name = 'material_administration.html'
    model = Materials
    context_object_name = 'materials'

class MaterialsCreateView(FormValidationMixin, FetchRequestMixin, CreateView):
    model = Materials
    form_class = MaterialsForm
    template_name = 'administration_forms.html'
    success_url = reverse_lazy('materials_administration')

class MaterialsUpdateView(FormValidationMixin, FetchRequestMixin, UpdateView):
    model = Materials
    form_class = MaterialsForm
    template_name = 'administration_forms.html'
    success_url = reverse_lazy('materials_administration')

class MaterialsDeleteView(FetchRequestMixin, View):
    http_method_names = ['delete']
    success_url = reverse_lazy('materials_administration')

    def delete(self, request: HttpRequest, pk, *args, **kwargs):
        material = get_object_or_404(Materials, id=pk)
        material.delete()
        return HttpResponseRedirect(self.success_url)


""" Season VIEWS """

class SeasonListView(ListView):
    template_name = 'season_administration.html'
    model = Season
    context_object_name = 'seasons'

class SeasonCreateView(FormValidationMixin, FetchRequestMixin, CreateView):
    model = Season
    form_class = SeasonForm
    template_name = 'administration_forms.html'
    success_url = reverse_lazy('season_administration')

class SeasonUpdateView(FormValidationMixin, FetchRequestMixin, UpdateView):
    model = Season
    form_class = SeasonForm
    template_name = 'administration_forms.html'
    success_url = reverse_lazy('season_administration')

class SeasonDeleteView(FetchRequestMixin, View):
    http_method_names = ['delete']
    success_url = reverse_lazy('season_administration')

    def delete(self, request: HttpRequest, pk, *args, **kwargs):
        season = get_object_or_404(Season, id=pk)
        season.delete()
        return HttpResponseRedirect(self.success_url)


""" Supplier VIEWS """

class SupplierListView(ListView):
    template_name = 'supplier_administration.html'
    model = Supplier
    context_object_name = 'suppliers'

class SupplierCreateView(FormValidationMixin, FetchRequestMixin, CreateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'administration_forms.html'
    success_url = reverse_lazy('supplier_administration')

class SupplierUpdateView(FormValidationMixin, FetchRequestMixin, UpdateView):    
    model = Supplier
    form_class = SupplierForm
    template_name = 'administration_forms.html'
    success_url = reverse_lazy('supplier_administration')

class SupplierDeleteView(FetchRequestMixin, View):
    http_method_names = ['delete']
    success_url = reverse_lazy('supplier_administration')

    def delete(self, request: HttpRequest, pk, *args, **kwargs):
        supplier = get_object_or_404(Supplier, id=pk)
        supplier.delete()
        return HttpResponseRedirect(self.success_url)
    

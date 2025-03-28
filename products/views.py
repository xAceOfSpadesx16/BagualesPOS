from typing import Any
from django.views.generic.base import View
from django.views.generic.edit import CreateView, DeleteView
from django.views.generic.list import ListView
from django.http import JsonResponse
from django.urls import reverse

from products.models import Product
from products.forms import ProductForm


class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'product_form.html'
    success_url = "administracion/productos/"
    

    # def form_valid(self, form):
    #     form.save()
    #     if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
    #         return JsonResponse({'success': True, 'redirect_url': self.get_success_url()})
    #     return super().form_valid(form)

    # def form_invalid(self, form):
    #     if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
    #         return JsonResponse({'success': False, 'errors': form.errors})
    #     return super().form_invalid(form)

class ProductDeleteView(DeleteView):
    ...

class ProductListView(ListView):
    ...

class ProductUpdateView(View):
    ...

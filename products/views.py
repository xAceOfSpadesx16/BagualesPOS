from typing import Any
from django.views.generic.base import View
from django.views.generic.edit import CreateView, DeleteView
from django.views.generic.list import ListView
from django.http import JsonResponse
from django.urls import reverse_lazy

from products.models import Product
from products.forms import ProductForm


class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'product_form.html'
    success_url = reverse_lazy('administration')

    def form_valid(self, form):
        super().form_valid
        form.save()
        return JsonResponse({'redirect_url': self.success_url }, status = 200)
    
    def form_invalid(self, form):
        response = super().form_invalid(form)
        response.status_code = 400
        return response

class ProductDeleteView(DeleteView):
    ...

class ProductListView(ListView):
    ...

class ProductUpdateView(View):
    ...

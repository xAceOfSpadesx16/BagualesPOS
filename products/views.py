from typing import Any
from django.views.generic.base import View
from django.views.generic.edit import CreateView, DeleteView
from django.views.generic.list import ListView
from django.http import JsonResponse

from products.models import Product
from products.forms import ProductForm



class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'product_form.html'
    extra_context = {
        'modal_title': 'Creacion de producto'
    }    
    

class ProductDeleteView(DeleteView):
    ...

class ProductListView(ListView):
    ...

class ProductUpdateView(View):
    ...
    
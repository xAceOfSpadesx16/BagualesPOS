from django.views.generic.list import ListView


from products.models import Product

class ProductsAdminView(ListView):
    template_name = 'product_administration.html'
    model = Product
    context_object_name = 'products'
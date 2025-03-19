from django.views.generic.base import TemplateView
from django.views.generic.list import ListView

from inventory.models import Inventory



# class InventoryIndex(TemplateView):
#     template_name = 'inventory.html'
    
    

class InventoryListView(ListView):
    template_name = 'inventory.html'
    model = Inventory
    queryset = Inventory.objects.select_related('product', 'product__brand')
    context_object_name = 'inventories'
    allow_empty = True
    ordering = ['product__brand__name']


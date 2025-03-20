from django.views.generic.base import View
from django.views.generic.list import ListView

from inventory.models import Inventory



class InventoryListView(ListView):
    template_name = 'inventory.html'
    model = Inventory
    queryset = Inventory.objects.sr_product_relateds()
    context_object_name = 'inventories'
    allow_empty = True
    ordering = ['product__brand__name']


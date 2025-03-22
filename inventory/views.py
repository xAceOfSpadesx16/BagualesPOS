from __future__ import annotations
from typing import TYPE_CHECKING

from django.views.generic.base import View
from django.views.generic.list import ListView
from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404
from json import loads

from inventory.models import Inventory

if TYPE_CHECKING:
    from django.http import HttpRequest
    

class InventoryListView(ListView):
    template_name = 'inventory.html'
    model = Inventory
    queryset = Inventory.objects.sr_product_relateds()
    context_object_name = 'inventories'
    allow_empty = True
    ordering = ['product__brand__name']

class UpdateInventoryView(View):

    http_method_names = ['patch']

    def dispatch(self, request, *args, **kwargs):
        if request.method.lower() == 'patch':
            return self.patch(request, *args, **kwargs)
        return super().dispatch(request, *args, **kwargs)
    
    def patch(self, request: HttpRequest, pk: int, *args, **kwargs):
        body = loads(request.body)

        try:
            quantity = int(body.get('quantity'))
        except ValueError:
            raise Http404('Cantidad no valida, ingrese un numero.')
        
        inventory: Inventory = get_object_or_404(inventory, id=pk)
        inventory.update_quantity(quantity=quantity)
        return JsonResponse({'success': True, 'message': 'Cantidad actualizada con exito.'})
    

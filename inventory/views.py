from __future__ import annotations
from typing import TYPE_CHECKING

from django.views.generic.base import View
from django.views.generic.list import ListView
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.db.models import F

from json import loads, JSONDecodeError
from enum import StrEnum

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

class UpdateOperation(StrEnum):
    ADDITION = 'addition'
    SUBTRACTION = 'subtraction'

    @classmethod
    def list_values(cls):
        return list(map(lambda c: c.value, cls))
    
    def __str__(self):
        return self.value
    
class InventoryQuantityUpdate(View):

    http_method_names = ['post']
    valid_operations = UpdateOperation.list_values()

    def post(self, request: HttpRequest, pk: int, *args, **kwargs):
        try:
            body = loads(request.body)
            operation = body.get('operation')
            quantity = int(body.get('quantity'))
        except JSONDecodeError:
            return JsonResponse(
                {'success': False, 'message': 'Cuerpo de solicitud inválido'}, 
                status=400
            )
        except (ValueError, TypeError):
            return JsonResponse(
                {'success': False, 'message': 'Formato de cantidad inválido'}, 
                status=400
            )

        if operation not in self.valid_operations:
            return JsonResponse({'success': False, 'message': 'Operación inválida.'}, status=400)
        
        if quantity < 0:
            return JsonResponse({'success': False, 'message': 'Cantidad inválida.'}, status=400)
        
        inventory = get_object_or_404(Inventory, id=pk)
        
        if operation == UpdateOperation.ADDITION:
            inventory.quantity = F('quantity') + quantity
            
        elif operation == UpdateOperation.SUBTRACTION:
            inventory.quantity = F('quantity') - quantity

        inventory.save()
        return JsonResponse({'success': True, 'message': 'Cantidad actualizada con exito.'})
    

from django.urls import path
from inventory.views import InventoryIndex

urlpatterns = [
    path('', InventoryIndex.as_view(), name='inventory'),
]
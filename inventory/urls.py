from django.urls import path
from inventory.views import InventoryListView, InventoryQuantityUpdate

urlpatterns = [
    path('', InventoryListView.as_view(), name='inventory'),
    path('update/<int:pk>/', InventoryQuantityUpdate.as_view(), name='inventory_update'),
]
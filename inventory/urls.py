from django.urls import path
from inventory.views import InventoryListView

urlpatterns = [
    path('', InventoryListView.as_view(), name='inventory'),
]
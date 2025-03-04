from django.urls import path
from sales.views import SaleDetailDelete, SaleDetailCreate, SaleDetailUpdate, SalesIndex, ProductAutocomplete



urlpatterns = [
    path('', SalesIndex.as_view(), name='sales'),
    path('delete-detail/<int:pk>/', SaleDetailDelete.as_view(), name='sale-detail-delete'),
    path('create-detail/', SaleDetailCreate.as_view(), name='sale-detail-create'),
    path('update-detail/<int:pk>/', SaleDetailUpdate.as_view(), name='sale-detail-update'),
    path('product-autocomplete/', ProductAutocomplete.as_view(), name='product-autocomplete'),
]
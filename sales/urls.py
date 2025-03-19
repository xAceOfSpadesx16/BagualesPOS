from django.urls import path
from sales.views import SaleDetailDelete, SaleDetailCreate, SaleQuantityDetailUpdate, SalesIndex, ProductAutocomplete



urlpatterns = [
    path('', SalesIndex.as_view(), name='sales'),
    path('create-detail/', SaleDetailCreate.as_view(), name='sale-detail-create'),
    path('update-detail-quantity/<int:pk>/', SaleQuantityDetailUpdate.as_view(), name='sale-detail-update'),
    path('delete-detail/<int:pk>/', SaleDetailDelete.as_view(), name='sale-detail-delete'),
    path('product-autocomplete/', ProductAutocomplete.as_view(), name='product-autocomplete'),
]
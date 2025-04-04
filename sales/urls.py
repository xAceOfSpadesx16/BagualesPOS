from django.urls import path
from sales.views import SaleDetailDelete, SaleDetailCreate, SaleQuantityDetailUpdate, SalesIndex, ProductAutocomplete, CloseSale




urlpatterns = [
    path('', SalesIndex.as_view(), name='sales'),
    path('create-detail/', SaleDetailCreate.as_view(), name='sale-detail-create'),
    path('update-detail-quantity/<int:pk>/', SaleQuantityDetailUpdate.as_view(), name='sale-detail-update'),
    path('delete-detail/<int:pk>/', SaleDetailDelete.as_view(), name='sale-detail-delete'),
    path('product-autocomplete/', ProductAutocomplete.as_view(), name='product-autocomplete'),
    path('close/', CloseSale.as_view(), name='close-sale'),
]

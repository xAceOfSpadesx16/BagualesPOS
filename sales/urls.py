from django.urls import path
from sales.views import SaleDetailDelete, SaleDetailCreate, SaleQuantityDetailUpdate, SalesIndex, ProductAutocomplete, CloseSale, CloseDetailsSale, ClientUpdateView




urlpatterns = [
    path('', SalesIndex.as_view(), name='sales'),
    path('create-detail/', SaleDetailCreate.as_view(), name='sale-detail-create'),
    path('update-detail-quantity/<int:pk>/', SaleQuantityDetailUpdate.as_view(), name='sale-detail-update'),
    path('delete-detail/<int:pk>/', SaleDetailDelete.as_view(), name='sale-detail-delete'),
    path('product-autocomplete/', ProductAutocomplete.as_view(), name='product-autocomplete'),
    path('close-details/<int:pk>/', CloseDetailsSale.as_view(), name='close-sale-details'),
    path('close/<int:pk>/', CloseSale.as_view(), name='close-sale'),
    path('update-client/<int:pk>/', ClientUpdateView.as_view(), name='update-client')
]

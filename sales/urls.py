from django.urls import path
from sales.views import *


urlpatterns = [
    path('', SalesIndex.as_view(), name='sales'),
    path('delete-detail/<int:pk>/', SaleDetailDelete.as_view(), name='sale-detail-delete'),
]
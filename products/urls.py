from django.urls import path
from products.views import ProductCreateView, ProductUpdateView
urlpatterns = [
    path('create/', ProductCreateView.as_view(), name='product_create'),
    path('update/<int:pk>/', ProductUpdateView.as_view(), name='product_update'),
]

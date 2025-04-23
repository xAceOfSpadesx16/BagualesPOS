from django.urls import path
from products.views import ProductCreateView, ProductUpdateView, ProductListView, ProductDeleteView


urlpatterns = []

product_patterns = [
    path('', ProductListView.as_view(), name='product_administration'),
    path('create/', ProductCreateView.as_view(), name='product_create'),
    path('update/<int:pk>/', ProductUpdateView.as_view(), name='product_update'),
    path('delete/<int:pk>/', ProductDeleteView.as_view(), name='product_delete'),
]

urlpatterns += product_patterns


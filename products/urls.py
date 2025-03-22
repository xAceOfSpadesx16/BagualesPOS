from django.urls import path
from products.views import ProductCreateView
urlpatterns = [
    path('create/', ProductCreateView.as_view(), name='product_create'),
    
]
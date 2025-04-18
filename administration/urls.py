from django.urls import path, include
from django.views.generic import RedirectView


urlpatterns = [
    path('', RedirectView.as_view(pattern_name='product_list', permanent=True), name='administration'),
    path('productos/', include('products.urls')),
]

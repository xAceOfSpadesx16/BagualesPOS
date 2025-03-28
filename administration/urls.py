from django.urls import path
from django.views.generic import RedirectView

from administration.views import ProductsAdminView


urlpatterns = [
    path('', RedirectView.as_view(pattern_name='products-administration', permanent=True), name='administration'),
    path('productos/', ProductsAdminView.as_view(), name='products-administration'),
]

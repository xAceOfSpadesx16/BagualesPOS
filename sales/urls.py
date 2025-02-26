from django.urls import path
from sales.views import *


urlpatterns = [
    path('', SalesIndex.as_view(), name='sales'),
]
from django.urls import path
from administration.views import AdministrationView

urlpatterns = [
    path('', AdministrationView.as_view(), name='administration'),
]
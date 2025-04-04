from django.urls import path
from clients.views import ClientAutocomplete

urlpatterns = [
    path('client-autocomplete/', ClientAutocomplete.as_view(), name='client-autocomplete'),
]
from django.urls import path
from clients.views import ClientAutocomplete, ClientsListView, ClientCCListView

urlpatterns = [
    path('', ClientsListView.as_view(), name='clients'),
    path('cc/', ClientCCListView.as_view(), name='clients_cc'),
    path('client-autocomplete/', ClientAutocomplete.as_view(), name='client-autocomplete'),
]
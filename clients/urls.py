from django.urls import path
from clients.views import ClientAutocomplete, ClientsListView, ClientRetrieveView, ClientCreateView, ClientDeleteView, ClientUpdateView, ClientRestoreView, BalanceRecordDetailView, CustomerAccountSoftDelete, CustomerAccountDetailView, CustomerAccountUpdateView, BalanceRecordCreateView

urlpatterns = [
    path('', ClientsListView.as_view(), name='clients'),
    path('<int:pk>/', ClientRetrieveView.as_view(), name='client_detail'),
    path('create/', ClientCreateView.as_view(), name='client_create'),
    path('update/<int:pk>/', ClientUpdateView.as_view(), name='client_update'),
    path('delete/<int:pk>/', ClientDeleteView.as_view(), name='client_soft_delete'),
    path('restore/<int:pk>/', ClientRestoreView.as_view(), name='client_restore'),
    path('autocomplete/', ClientAutocomplete.as_view(), name='client_autocomplete'),
    path('cc/<int:pk>/', CustomerAccountDetailView.as_view(), name='customer_account_detail'),
    path('cc/<int:pk>/delete/', CustomerAccountSoftDelete.as_view(), name='customer_account_soft_delete'),
    path('cc/<int:pk>/update/', CustomerAccountUpdateView.as_view(), name='customer_account_update'),
    path('cc/<int:pk>/record/create/', BalanceRecordCreateView.as_view(), name='balance_record_create'),
    path('cc/record/<int:pk>/', BalanceRecordDetailView.as_view(), name='balance_record_detail'),
]
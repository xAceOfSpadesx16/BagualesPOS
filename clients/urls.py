from django.urls import path
from clients.views import ClientAutocomplete, ClientsListView, BalanceRecordCreateAPI, BalanceRecordDetailView, BalanceRecordListView, CustomerAccountSoftDelete

urlpatterns = [
    path('', ClientsListView.as_view(), name='clients'),
    path('client-autocomplete/', ClientAutocomplete.as_view(), name='client-autocomplete'),
    path('cc/<int:customer_account_id>/records/', BalanceRecordListView.as_view(), name='customer_account_balance_record_list'),
    path('cc/record/<int:pk>/', BalanceRecordDetailView.as_view(), name='balance_record_detail'),
    path('cc/record/create/', BalanceRecordCreateAPI.as_view(), name='balance_record_create_api'),
    path('cc/record/delete/<int:customer_account_id>/', CustomerAccountSoftDelete.as_view(), name='balance_record_delete_api'),
]
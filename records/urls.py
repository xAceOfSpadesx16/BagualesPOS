from django.urls import path
from records.views import RecordsIndex

urlpatterns = [
    path('', RecordsIndex.as_view(), name='records'),
]
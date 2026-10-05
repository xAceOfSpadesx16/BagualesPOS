from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClientViewSet, CustomerAccountViewSet, CustomerBalanceRecordViewSet

router = DefaultRouter()
router.register(r'clients', ClientViewSet)
router.register(r'customer-accounts', CustomerAccountViewSet)
router.register(r'balance-records', CustomerBalanceRecordViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
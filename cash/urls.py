from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CashRegisterViewSet, CashSessionViewSet, CashMovementViewSet

router = DefaultRouter()
router.register(r'cash-registers', CashRegisterViewSet, basename='cashregister')
router.register(r'cash-sessions', CashSessionViewSet, basename='cashsession')
router.register(r'cash-movements', CashMovementViewSet, basename='cashmovement')

urlpatterns = [
    path('cash/', include(router.urls)),
]

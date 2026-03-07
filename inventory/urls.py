from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InventoryViewSet, StockAdjustmentRequestViewSet, StockMovementViewSet

router = DefaultRouter()
router.register(r'inventory', InventoryViewSet)
router.register(r'stock-adjustments', StockAdjustmentRequestViewSet, basename='stockadjustmentrequest')
router.register(r'stock-movements', StockMovementViewSet, basename='stockmovement')

urlpatterns = [
    path('', include(router.urls)),
]
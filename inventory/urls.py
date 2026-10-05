from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InventoryViewSet, StockAdjustmentRequestViewSet, StockMovementViewSet, StockTransferViewSet

router = DefaultRouter()
router.register(r'inventory', InventoryViewSet)
router.register(r'stock-adjustments', StockAdjustmentRequestViewSet, basename='stockadjustmentrequest')
router.register(r'stock-movements', StockMovementViewSet, basename='stockmovement')
router.register(r'stock-transfers', StockTransferViewSet, basename='stocktransfer')

urlpatterns = [
    path('', include(router.urls)),
]
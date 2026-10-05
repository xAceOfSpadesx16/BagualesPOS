from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SaleViewSet, SaleDetailViewSet, PayMethodViewSet, ReturnViewSet

router = DefaultRouter()
router.register(r'sales', SaleViewSet)
router.register(r'sale-details', SaleDetailViewSet)
router.register(r'pay-methods', PayMethodViewSet)
router.register(r'returns', ReturnViewSet, basename='return')

urlpatterns = [
    path('', include(router.urls)),
]

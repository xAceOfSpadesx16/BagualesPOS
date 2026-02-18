from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SaleViewSet, SaleDetailViewSet, PayMethodViewSet

router = DefaultRouter()
router.register(r'sales', SaleViewSet)
router.register(r'sale-details', SaleDetailViewSet)
router.register(r'pay-methods', PayMethodViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

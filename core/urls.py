from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BranchViewSet

# Create router and register viewsets
router = DefaultRouter()
router.register(r'branches', BranchViewSet, basename='branch')

urlpatterns = [
    path('', include(router.urls)),
]

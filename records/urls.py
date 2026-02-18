from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RecordsViewSet

router = DefaultRouter()
router.register(r'records', RecordsViewSet, basename='records')

urlpatterns = [
    path('', include(router.urls)),
]
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuditRecordViewSet

router = DefaultRouter()
router.register(r'records', AuditRecordViewSet, basename='auditrecord')

urlpatterns = [
    path('', include(router.urls)),
]

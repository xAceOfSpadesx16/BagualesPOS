from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BranchViewSet, CompanyProfileView, CompanySettingsView

router = DefaultRouter()
router.register(r'branches', BranchViewSet, basename='branch')

urlpatterns = [
    path('', include(router.urls)),
    path('company/me/', CompanyProfileView.as_view(), name='company-me'),
    path('company/settings/', CompanySettingsView.as_view(), name='company-settings'),
]

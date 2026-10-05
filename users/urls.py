from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, AuthorizationCodeViewSet, CustomTokenObtainPairView, LogoutView
from rest_framework_simplejwt.views import TokenRefreshView

router = DefaultRouter()
router.register(r'users/authorization-codes', AuthorizationCodeViewSet, basename='authorization-codes')
router.register(r'users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/logout/', LogoutView.as_view(), name='token_logout'),
]
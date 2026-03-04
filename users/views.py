from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAdminUser
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, CustomTokenObtainPairSerializer, UserRegistrationSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import action

User = get_user_model()

class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = (AllowAny,)
    serializer_class = CustomTokenObtainPairSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    ordering = ['-date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['date_joined', 'username']
    
    def get_queryset(self):
        """
        Filter users by the current user's company to prevent cross-tenant data leakage.
        """
        user = self.request.user
        if getattr(self, 'swagger_fake_view', False):
            return User.objects.none()
            
        if not user.is_authenticated:
            return User.objects.none()

        if user.is_superuser:
            return User.objects.all()

        if hasattr(user, 'company') and user.company:
            return User.objects.filter(company=user.company)
            
        if hasattr(user, 'owned_company') and user.owned_company:
            return User.objects.filter(company=user.owned_company)

        return User.objects.none()
    
    def get_permissions(self):
        """
        Allow registration without authentication.
        """
        if self.action == 'register':
            return [AllowAny()]
        return super().get_permissions()
    
    @action(detail=False, methods=['post'], url_path='register')
    def register(self, request):
        """
        Register a new user with automatic company creation.
        
        POST /api/users/register/
        {
            "username": "john_doe",
            "email": "john@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "password": "securepassword",
            "password_confirm": "securepassword",
            "company_name": "Acme Corp",
            "company_tax_id": "12345678"
        }
        """
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'company_id': user.company.id if user.company else None,
                'company_name': user.company.name if user.company else None,
                'message': 'User registered successfully'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAdminUser, BasePermission
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, CustomTokenObtainPairSerializer, UserRegistrationSerializer, EmployeeSerializer, RoleSerializer
from django.contrib.auth.models import Group
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import action

User = get_user_model()


class IsAdminOrManager(BasePermission):
    """
    Permission class that allows only users with 'Administrador General' or 'Gerente' roles.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Superusers always have permission
        if request.user.is_superuser:
            return True
        
        # Check if user has the required roles
        return request.user.groups.filter(
            name__in=['Administrador General', 'Gerente']
        ).exists()

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
        Filter users by the current user's company and branch to prevent cross-tenant data leakage.
        - Superusers: see all users
        - Company owners (General Admins): see all users in their company
        - Branch managers/employees: see only users assigned to their branches
        """
        user = self.request.user
        if getattr(self, 'swagger_fake_view', False):
            return User.objects.none()
            
        if not user.is_authenticated:
            return User.objects.none()

        if user.is_superuser:
            return User.objects.all()

        # Check if user is company owner (General Admin)
        if hasattr(user, 'owned_company') and user.owned_company:
            return User.objects.filter(company=user.owned_company)

        # Regular users (Branch Managers/Employees) see only users in their branches
        if hasattr(user, 'company') and user.company:
            user_branches = user.branch.all()
            if user_branches.exists():
                # Return users that share at least one branch with the current user
                return User.objects.filter(company=user.company, branch__in=user_branches).distinct()
            # If user has no branches, show all company users (fallback)
            return User.objects.filter(company=user.company)

        return User.objects.none()
    
    def get_permissions(self):
        """
        Allow registration without authentication.
        Allow employee management only for admins and managers.
        """
        if self.action == 'register':
            return [AllowAny()]
        if self.action in ['create_employee', 'update_employee']:
            return [IsAdminOrManager()]
        if self.action == 'roles':
            return [IsAuthenticated()]
        return super().get_permissions()
    
    def get_serializer_class(self):
        """
        Return different serializers based on action.
        """
        if self.action == 'register':
            return UserRegistrationSerializer
        if self.action in ['create_employee', 'update_employee']:
            return EmployeeSerializer
        return UserSerializer
    
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
    
    @action(detail=False, methods=['post'], url_path='employees')
    def create_employee(self, request):
        """
        Create a new employee user within the authenticated user's company.
        Only users with 'Administrador General' or 'Gerente' roles can create employees.
        
        POST /api/users/employees/
        {
            "username": "employee1",
            "email": "employee@example.com",
            "first_name": "Jane",
            "last_name": "Smith",
            "password": "securepassword",
            "password_confirm": "securepassword",
            "groups_ids": [1, 2],
            "branches_ids": [1]
        }
        """
        if not hasattr(request.user, 'company') or not request.user.company:
            return Response(
                {'error': 'You must belong to a company to create employees.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Pass company in context to serializer
        serializer = EmployeeSerializer(
            data=request.data,
            context={'request': request, 'company': request.user.company}
        )
        
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'company_id': user.company.id if user.company else None,
                'groups': [group.name for group in user.groups.all()],
                'branches': [branch.name for branch in user.branch.all()],
                'message': 'Employee created successfully'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['put', 'patch'], url_path='employee')
    def update_employee(self, request, pk=None):
        """
        Update an existing employee user.
        Only users with 'Administrador General' or 'Gerente' roles can update employees.
        
        PUT/PATCH /api/users/{id}/employee/
        {
            "first_name": "Jane",
            "last_name": "Doe",
            "groups_ids": [1],
            "branches_ids": [1, 2]
        }
        """
        user = self.get_object()
        
        # Ensure the employee belongs to the same company
        if not hasattr(request.user, 'company') or not request.user.company:
            return Response(
                {'error': 'You must belong to a company.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if user.company != request.user.company:
            return Response(
                {'error': 'You can only update employees from your company.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Pass company in context to serializer
        serializer = EmployeeSerializer(
            user,
            data=request.data,
            partial=request.method == 'PATCH',
            context={'request': request, 'company': request.user.company}
        )
        
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'groups': [group.name for group in user.groups.all()],
                'branches': [branch.name for branch in user.branch.all()],
                'message': 'Employee updated successfully'
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def roles(self, request):
        """
        Returns the list of available roles (groups) to assign to employees.
        If the user is not an 'Administrador General', it excludes 'Administrador General' from the list.
        """
        # Validate user is authenticated
        if not request.user or not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
            
        groups = Group.objects.all().order_by('id')
        
        # If the requester is not an 'Administrador General', don't let them see/choose it
        if not request.user.groups.filter(name='Administrador General').exists():
            groups = groups.exclude(name='Administrador General')
            
        serializer = RoleSerializer(groups, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


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

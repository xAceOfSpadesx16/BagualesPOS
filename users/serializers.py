from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import transaction
from .models import Profile, AuthorizationCode
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from core.models import Company, Branch

User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['id'] = user.id
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        if user.company:
            token['company_id'] = user.company.id
            token['company_name'] = user.company.name

        return token

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)
    groups_names = serializers.SerializerMethodField()
    branches_names = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'date_joined', 'profile', 'company', 'groups_names', 'branches_names']
        read_only_fields = ['date_joined', 'last_login']
    
    def get_groups_names(self, obj):
        """Return list of group names for this user."""
        return [group.name for group in obj.groups.all()]
    
    def get_branches_names(self, obj):
        """Return list of branch names for this user."""
        return [branch.name for branch in obj.branch.all()]


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration with automatic company creation.
    Creates a new user and company, linking them together.
    """
    password = serializers.CharField(write_only=True, required=True)
    password_confirm = serializers.CharField(write_only=True, required=True)
    company_name = serializers.CharField(write_only=True, required=True)
    company_tax_id = serializers.CharField(write_only=True, required=False, allow_blank=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'password_confirm', 'company_name', 'company_tax_id']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    @transaction.atomic
    def create(self, validated_data):
        # Extract company and password data
        company_name = validated_data.pop('company_name')
        company_tax_id = validated_data.pop('company_tax_id', '')
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        # Create user (without company yet)
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            password=password
        )
        
        # Create company with temporary owner=None
        company = Company.objects.create(
            name=company_name,
            tax_id=company_tax_id if company_tax_id else None,
            is_active=True
        )
        
        # Link user to company
        user.company = company
        user.save()
        
        # Set user as company owner
        company.owner = user
        company.save()
        
        # Assign "Administrador General" role to the newly registered user
        admin_group, _ = Group.objects.get_or_create(name='Administrador General')
        user.groups.add(admin_group)
        
        return user


class EmployeeSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and managing employee users.
    
    Allows administrators to create users within their company,
    assigning roles (groups) and branches.
    """
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    groups_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text="List of group IDs to assign to the user"
    )
    branches_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text="List of branch IDs to assign to the user"
    )
    groups_names = serializers.SerializerMethodField(read_only=True)
    branches_names = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'password', 'password_confirm', 'is_active',
            'groups_ids', 'branches_ids', 'groups_names', 'branches_names',
            'company', 'date_joined'
        ]
        read_only_fields = ['id', 'company', 'date_joined']
    
    def get_groups_names(self, obj):
        """Return list of group names for this user."""
        return [group.name for group in obj.groups.all()]
    
    def get_branches_names(self, obj):
        """Return list of branch names for this user."""
        return [branch.name for branch in obj.branch.all()]
    
    def validate(self, attrs):
        """Validate password confirmation."""
        if attrs.get('password') != attrs.get('password_confirm'):
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def validate_groups_ids(self, value):
        """
        Validate that all group IDs exist and prevent assignment of 'Administrador General'
        role unless the requesting user is also an 'Administrador General'.
        """
        if not value:
            return value
        
        # Verify all groups exist
        groups = Group.objects.filter(id__in=value)
        if groups.count() != len(value):
            raise serializers.ValidationError("One or more group IDs are invalid.")
        
        # Check if trying to assign "Administrador General" role
        admin_general = groups.filter(name='Administrador General').first()
        if admin_general:
            request_user = self.context.get('request').user if self.context.get('request') else None
            if not request_user or not request_user.groups.filter(name='Administrador General').exists():
                raise serializers.ValidationError(
                    "Only users with 'Administrador General' role can assign this role to others."
                )
        
        return value
    
    def validate_branches_ids(self, value):
        """Validate that all branch IDs exist and belong to the user's company."""
        if not value:
            return value
        
        request_user = self.context.get('request').user if self.context.get('request') else None
        if not request_user or not request_user.company:
            raise serializers.ValidationError("Unable to validate branches: user has no company.")
        
        # Verify all branches exist and belong to the user's company
        branches = Branch.objects.filter(id__in=value, company=request_user.company)
        if branches.count() != len(value):
            raise serializers.ValidationError(
                "One or more branch IDs are invalid or don't belong to your company."
            )
        
        return value
    
    @transaction.atomic
    def create(self, validated_data):
        """
        Create employee user with assigned groups and branches.
        Company is automatically set from context (request.user.company).
        """
        # Extract many-to-many fields
        groups_ids = validated_data.pop('groups_ids', [])
        branches_ids = validated_data.pop('branches_ids', [])
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        # Get company from context (set by view)
        company = self.context.get('company')
        if not company:
            raise serializers.ValidationError({
                'company': 'Unable to determine company from context.'
            })
        
        # Create user
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            password=password,
            company=company,
            is_active=validated_data.get('is_active', True)
        )
        
        # Assign groups
        if groups_ids:
            groups = Group.objects.filter(id__in=groups_ids)
            user.groups.set(groups)
        
        # Assign branches
        if branches_ids:
            branches = Branch.objects.filter(id__in=branches_ids, company=company)
            user.branch.set(branches)
        
        return user
    
    @transaction.atomic
    def update(self, instance, validated_data):
        """
        Update employee user.
        Password and company cannot be changed through this serializer.
        """
        # Extract many-to-many fields
        groups_ids = validated_data.pop('groups_ids', None)
        branches_ids = validated_data.pop('branches_ids', None)
        validated_data.pop('password', None)
        validated_data.pop('password_confirm', None)
        
        # Update basic fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update groups if provided
        if groups_ids is not None:
            groups = Group.objects.filter(id__in=groups_ids)
            instance.groups.set(groups)
        
        # Update branches if provided
        if branches_ids is not None:
            company = self.context.get('company') or instance.company
            branches = Branch.objects.filter(id__in=branches_ids, company=company)
            instance.branch.set(branches)
        
        return instance


# --- Authorization Code Serializers ---

class ApiUserBriefSerializer(serializers.ModelSerializer):
    """Datos minimos del usuario para nested responses."""
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'email']
        read_only_fields = fields


class AuthorizationCodeSerializer(serializers.ModelSerializer):
    """Serializer de lectura para codigos de autorizacion."""
    user_data = ApiUserBriefSerializer(source='user', read_only=True)

    class Meta:
        model = AuthorizationCode
        fields = ['id', 'user', 'user_data', 'code', 'label', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class AuthorizationCodeCreateSerializer(serializers.ModelSerializer):
    """Serializer de escritura para crear codigos de autorizacion."""

    class Meta:
        model = AuthorizationCode
        fields = ['user', 'code', 'label', 'is_active']

    def validate_code(self, value: str) -> str:
        """Valida que el codigo no exista para la misma empresa."""
        company = self.context.get('company')
        if company and AuthorizationCode.objects.filter(company=company, code=value).exists():
            raise serializers.ValidationError('Ya existe un codigo de autorizacion con ese valor en esta empresa.')
        return value

    def validate_user(self, value) -> object:
        """Valida que el usuario pertenezca a la misma empresa."""
        company = self.context.get('company')
        if company and value.company != company:
            raise serializers.ValidationError('El usuario no pertenece a la misma empresa.')
        return value

    def create(self, validated_data: dict) -> AuthorizationCode:
        company = self.context.get('company')
        validated_data['company'] = company
        return super().create(validated_data)


class ValidateAuthorizationCodeSerializer(serializers.Serializer):
    """Serializer para validar un codigo de autorizacion via escaneo."""
    code = serializers.CharField(required=True, max_length=50)

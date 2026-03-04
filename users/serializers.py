from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db import transaction
from .models import Profile
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from core.models import Company

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

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'date_joined', 'profile', 'company']
        read_only_fields = ['date_joined', 'last_login']


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
        
        return user

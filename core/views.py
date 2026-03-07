from rest_framework import viewsets, status, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_multitenant.utils import set_current_tenant
from .models import Company, Branch
from .serializers import CompanySerializer, BranchSerializer, BranchListSerializer


class BranchViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing branches with multi-tenant isolation.
    
    Automatically filters branches by the authenticated user's company
    and sets the company when creating new branches.
    
    List action uses BranchListSerializer for performance.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = BranchSerializer
    ordering = ['name']
    search_fields = ['name', 'code', 'address']
    filterset_fields = ['is_active']
    
    def get_queryset(self):
        """
        Filter branches by the current user's company.
        Implements multi-tenant data isolation.
        """
        user = self.request.user
        
        # Handle Swagger/OpenAPI schema generation
        if getattr(self, 'swagger_fake_view', False):
            return Branch.objects.none()
        
        if not user.is_authenticated:
            return Branch.objects.none()
        
        # Superusers can see all branches
        if user.is_superuser:
            return Branch.objects.all()
        
        # Regular users only see branches from their company
        if hasattr(user, 'company') and user.company:
            return Branch.objects.filter(company=user.company)
        
        return Branch.objects.none()
    
    def get_serializer_class(self):
        """
        Use lightweight serializer for list action.
        """
        if self.action == 'list':
            return BranchListSerializer
        return BranchSerializer
    
    def perform_create(self, serializer):
        """
        Automatically assign the company from the authenticated user.
        Enforces multi-tenant isolation by preventing users from creating
        branches for other companies.
        """
        user = self.request.user
        
        if not hasattr(user, 'company') or not user.company:
            raise serializers.ValidationError({
                'company': 'User must belong to a company to create branches.'
            })
        
        # Set current tenant for django-multitenant
        set_current_tenant(user.company)
        
        # Save with user's company (ignore any company field in request data)
        serializer.save(company=user.company)
    
    def perform_update(self, serializer):
        """
        Ensure company cannot be changed during update.
        """
        user = self.request.user
        
        if hasattr(user, 'company') and user.company:
            set_current_tenant(user.company)
        
        # Ensure company remains the same
        serializer.save(company=serializer.instance.company)

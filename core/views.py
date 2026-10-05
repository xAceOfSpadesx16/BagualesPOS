from rest_framework import viewsets, serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django_multitenant.utils import set_current_tenant
from .models import Branch, CompanySettings
from .serializers import (
    CompanyProfileSerializer,
    CompanySettingsSerializer,
    BranchSerializer,
    BranchListSerializer,
)


class CompanyProfileView(APIView):
    """GET /api/company/me/ — Perfil de la empresa del usuario autenticado."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        company = None

        if hasattr(user, 'owned_company') and user.owned_company:
            company = user.owned_company
        elif hasattr(user, 'company') and user.company:
            company = user.company

        if not company:
            return Response(
                {'status': 404, 'message': 'No company associated with this user.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = CompanyProfileSerializer(company)
        return Response(serializer.data)


class CompanySettingsView(APIView):
    """GET/PATCH /api/company/settings/ — Configuración de la empresa."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        company = self._get_company(request)
        if not company:
            return Response(
                {'status': 404, 'message': 'No company associated with this user.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Crea settings por defecto si no existen
        settings, _ = CompanySettings.objects.get_or_create(company=company)
        return Response(CompanySettingsSerializer(settings).data)

    def patch(self, request):
        company = self._get_company(request)
        if not company:
            return Response(
                {'status': 404, 'message': 'No company associated with this user.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        settings, _ = CompanySettings.objects.get_or_create(company=company)
        serializer = CompanySettingsSerializer(settings, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def _get_company(self, request):
        user = request.user
        if hasattr(user, 'owned_company') and user.owned_company:
            return user.owned_company
        if hasattr(user, 'company') and user.company:
            return user.company
        return None


class BranchViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing branches with multi-tenant isolation.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = BranchSerializer
    ordering = ['name']
    search_fields = ['name', 'code', 'address']
    filterset_fields = ['is_active']

    def get_queryset(self):
        user = self.request.user

        if getattr(self, 'swagger_fake_view', False):
            return Branch.objects.none()

        if not user.is_authenticated:
            return Branch.objects.none()

        if user.is_superuser:
            return Branch.objects.all()

        if hasattr(user, 'company') and user.company:
            return Branch.objects.filter(company=user.company)

        return Branch.objects.none()

    def get_serializer_class(self):
        if self.action == 'list':
            return BranchListSerializer
        return BranchSerializer

    def perform_create(self, serializer):
        user = self.request.user

        if not hasattr(user, 'company') or not user.company:
            raise serializers.ValidationError({
                'company': 'User must belong to a company to create branches.'
            })

        set_current_tenant(user.company)
        serializer.save(company=user.company)

    def perform_update(self, serializer):
        user = self.request.user

        if hasattr(user, 'company') and user.company:
            set_current_tenant(user.company)

        serializer.save(company=serializer.instance.company)

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count
from django.db.models.functions import ExtractHour
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from utils.mixins import TenantViewSetMixin
from .models import AuditRecord
from .serializers import AuditRecordSerializer


class AuditRecordViewSet(TenantViewSetMixin, viewsets.ReadOnlyModelViewSet):
    """ViewSet de solo lectura para registros de auditoría."""
    queryset = AuditRecord.objects.select_related(
        'company', 'branch', 'user'
    ).order_by('-created_at')

    serializer_class = AuditRecordSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['action', 'branch', 'user']
    search_fields = ['description']
    ordering_fields = ['created_at', 'action']

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        GET /api/records/summary/
        Resumen agregado de auditoría con filtros de fecha.
        """
        queryset = self.filter_queryset(self.get_queryset())

        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)

        by_action = queryset.values('action').annotate(count=Count('id'))
        by_user = queryset.values('user', 'user__first_name', 'user__last_name').annotate(
            count=Count('id')
        )
        by_hour = queryset.annotate(hour=ExtractHour('created_at')).values('hour').annotate(
            count=Count('id')
        ).order_by('hour')

        return Response({
            'total_records': queryset.count(),
            'by_action': [
                {'action': item['action'], 'count': item['count']}
                for item in by_action
            ],
            'by_user': [
                {
                    'user_id': item['user'],
                    'user_name': f"{item['user__first_name']} {item['user__last_name']}".strip(),
                    'count': item['count'],
                }
                for item in by_user if item['user']
            ],
            'most_active_hours': [
                {'hour': item['hour'], 'count': item['count']}
                for item in by_hour
            ],
        })

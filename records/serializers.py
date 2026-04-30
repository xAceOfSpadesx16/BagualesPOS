from rest_framework import serializers
from .models import AuditRecord


class AuditRecordSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True, default='')
    branch_name = serializers.CharField(source='branch.name', read_only=True, default='')
    action_display = serializers.CharField(source='get_action_display', read_only=True)

    class Meta:
        model = AuditRecord
        fields = [
            'id', 'company', 'branch', 'branch_name',
            'user', 'user_name', 'action', 'action_display',
            'ip_address', 'description', 'details', 'created_at',
        ]
        read_only_fields = fields

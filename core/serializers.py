from rest_framework import serializers
from .models import Company, Branch, CompanySettings


class CompanySerializer(serializers.ModelSerializer):
    branches_count = serializers.IntegerField(source='branches.count', read_only=True)

    class Meta:
        model = Company
        fields = [
            'id', 'name', 'legal_name', 'tax_id', 'logo',
            'address', 'phone', 'email', 'is_active',
            'branches_count', 'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']


class CompanyProfileSerializer(serializers.ModelSerializer):
    """Serializer de solo lectura para el perfil de empresa."""

    class Meta:
        model = Company
        fields = [
            'id', 'name', 'legal_name', 'tax_id', 'logo',
            'address', 'phone', 'email', 'is_active',
        ]
        read_only_fields = fields


class CompanySettingsSerializer(serializers.ModelSerializer):

    class Meta:
        model = CompanySettings
        fields = [
            'id', 'company',
            'tax_name', 'tax_rate', 'tax_enabled',
            'currency_code', 'currency_symbol', 'currency_decimals',
            'receipt_header', 'receipt_footer', 'receipt_show_tax',
            'allow_negative_stock', 'low_stock_threshold',
        ]
        read_only_fields = ['company', 'id']


class BranchSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)

    class Meta:
        model = Branch
        fields = [
            'id', 'company', 'company_name', 'name', 'code',
            'address', 'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['company', 'created_at', 'updated_at']

    def validate_code(self, value: str) -> str:
        if self.instance:
            if Branch.objects.exclude(pk=self.instance.pk).filter(code=value).exists():
                raise serializers.ValidationError("A branch with this code already exists.")
        else:
            if Branch.objects.filter(code=value).exists():
                raise serializers.ValidationError("A branch with this code already exists.")
        return value


class BranchListSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)

    class Meta:
        model = Branch
        fields = ['id', 'name', 'code', 'company_name', 'is_active']

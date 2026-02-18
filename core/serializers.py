from rest_framework import serializers
from .models import Company, Branch


class CompanySerializer(serializers.ModelSerializer):
    """
    Serializer for Company model
    """
    branches_count = serializers.IntegerField(source='branches.count', read_only=True)
    
    class Meta:
        model = Company
        fields = [
            'id',
            'name',
            'tax_id',
            'logo',
            'is_active',
            'branches_count',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class BranchSerializer(serializers.ModelSerializer):
    """
    Serializer for Branch model
    """
    company_name = serializers.CharField(source='company.name', read_only=True)
    
    class Meta:
        model = Branch
        fields = [
            'id',
            'company',
            'company_name',
            'name',
            'code',
            'address',
            'is_active',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate_code(self, value):
        """
        Validate that code is unique
        """
        if self.instance:
            # Update case - exclude current instance
            if Branch.objects.exclude(pk=self.instance.pk).filter(code=value).exists():
                raise serializers.ValidationError("A branch with this code already exists.")
        else:
            # Create case
            if Branch.objects.filter(code=value).exists():
                raise serializers.ValidationError("A branch with this code already exists.")
        return value


class BranchListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing branches
    """
    company_name = serializers.CharField(source='company.name', read_only=True)
    
    class Meta:
        model = Branch
        fields = ['id', 'name', 'code', 'company_name', 'is_active']

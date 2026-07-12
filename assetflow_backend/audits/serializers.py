from rest_framework import serializers

from accounts.serializers import EmployeeMiniSerializer
from .models import AuditCycle, AuditItem


class AuditItemSerializer(serializers.ModelSerializer):
    asset_tag = serializers.CharField(source='asset.tag', read_only=True)
    asset_name = serializers.CharField(source='asset.name', read_only=True)
    is_discrepancy = serializers.ReadOnlyField()

    class Meta:
        model = AuditItem
        fields = [
            'id', 'cycle', 'asset', 'asset_tag', 'asset_name', 'expected_location',
            'verification', 'notes', 'is_discrepancy', 'verified_by', 'verified_at',
        ]
        read_only_fields = ['id', 'verified_by', 'verified_at']


class AuditCycleSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True, default=None)
    auditors_detail = EmployeeMiniSerializer(source='auditors', many=True, read_only=True)
    item_count = serializers.IntegerField(source='items.count', read_only=True)
    discrepancy_count = serializers.SerializerMethodField()

    class Meta:
        model = AuditCycle
        fields = [
            'id', 'name', 'department', 'department_name', 'auditors', 'auditors_detail',
            'start_date', 'end_date', 'status', 'item_count', 'discrepancy_count',
            'created_at', 'closed_at',
        ]
        read_only_fields = ['id', 'status', 'created_at', 'closed_at']

    def get_discrepancy_count(self, obj):
        return obj.items.filter(verification__in=[AuditItem.Verification.MISSING, AuditItem.Verification.DAMAGED]).count()

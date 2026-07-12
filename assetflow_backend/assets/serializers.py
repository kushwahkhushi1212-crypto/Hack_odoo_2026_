from rest_framework import serializers

from accounts.serializers import EmployeeMiniSerializer
from .models import AllocationHistory, Asset


class AssetSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True, default=None)
    current_holder_detail = EmployeeMiniSerializer(source='current_holder', read_only=True)
    is_idle = serializers.ReadOnlyField()

    class Meta:
        model = Asset
        fields = [
            'id', 'tag', 'name', 'category', 'category_name', 'status', 'department',
            'department_name', 'current_holder', 'current_holder_detail', 'location',
            'qr_code', 'purchase_date', 'purchase_value', 'service_due_date', 'notes',
            'is_idle', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'tag', 'qr_code', 'created_at', 'updated_at']

    def validate_status(self, value):
        # Status is normally driven by transfer/maintenance workflows, but an
        # admin may still correct it directly (e.g. marking something retired).
        return value


class AllocationHistorySerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.get_full_name', read_only=True, default=None)
    department_name = serializers.CharField(source='department.name', read_only=True, default=None)

    class Meta:
        model = AllocationHistory
        fields = ['id', 'asset', 'employee', 'employee_name', 'department',
                  'department_name', 'action', 'condition', 'notes', 'occurred_at']
        read_only_fields = ['id', 'occurred_at']

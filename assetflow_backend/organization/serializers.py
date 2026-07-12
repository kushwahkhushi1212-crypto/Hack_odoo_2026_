from rest_framework import serializers

from .models import Category, Department


class DepartmentSerializer(serializers.ModelSerializer):
    head_name = serializers.CharField(source='head.get_full_name', read_only=True, default=None)
    parent_name = serializers.CharField(source='parent.name', read_only=True, default=None)
    employee_count = serializers.IntegerField(source='employees.count', read_only=True)

    class Meta:
        model = Department
        fields = ['id', 'name', 'code', 'head', 'head_name', 'parent', 'parent_name',
                  'is_active', 'employee_count', 'created_at']
        read_only_fields = ['id', 'created_at']


class CategorySerializer(serializers.ModelSerializer):
    asset_count = serializers.IntegerField(source='assets.count', read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'is_active', 'asset_count', 'created_at']
        read_only_fields = ['id', 'created_at']

from rest_framework import serializers

from accounts.serializers import EmployeeMiniSerializer
from assets.models import Asset
from .models import TransferRequest


class TransferRequestSerializer(serializers.ModelSerializer):
    asset_tag = serializers.CharField(source='asset.tag', read_only=True)
    asset_name = serializers.CharField(source='asset.name', read_only=True)
    from_employee_detail = EmployeeMiniSerializer(source='from_employee', read_only=True)
    to_employee_detail = EmployeeMiniSerializer(source='to_employee', read_only=True)
    requested_by_detail = EmployeeMiniSerializer(source='requested_by', read_only=True)

    class Meta:
        model = TransferRequest
        fields = [
            'id', 'asset', 'asset_tag', 'asset_name', 'from_employee', 'from_employee_detail',
            'to_employee', 'to_employee_detail', 'reason', 'status', 'requested_by',
            'requested_by_detail', 'resolved_by', 'created_at', 'resolved_at',
        ]
        read_only_fields = ['id', 'status', 'requested_by', 'resolved_by', 'created_at', 'resolved_at']

    def validate(self, attrs):
        asset = attrs.get('asset') or getattr(self.instance, 'asset', None)
        to_employee = attrs.get('to_employee')
        if asset and asset.status == Asset.Status.MAINTENANCE:
            raise serializers.ValidationError('Asset is under maintenance and cannot be transferred.')
        if asset and asset.current_holder_id and to_employee and asset.current_holder_id == to_employee.id:
            raise serializers.ValidationError('Asset is already allocated to this employee.')
        return attrs

    def create(self, validated_data):
        asset = validated_data['asset']
        validated_data['from_employee'] = asset.current_holder
        return super().create(validated_data)


class TransferDecisionSerializer(serializers.Serializer):
    """Body for the approve/reject action endpoints."""
    notes = serializers.CharField(required=False, allow_blank=True)

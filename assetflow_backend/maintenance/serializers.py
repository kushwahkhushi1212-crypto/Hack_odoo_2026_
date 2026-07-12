from rest_framework import serializers

from accounts.serializers import EmployeeMiniSerializer
from .models import MaintenanceTicket


class MaintenanceTicketSerializer(serializers.ModelSerializer):
    asset_tag = serializers.CharField(source='asset.tag', read_only=True)
    asset_name = serializers.CharField(source='asset.name', read_only=True)
    reported_by_detail = EmployeeMiniSerializer(source='reported_by', read_only=True)
    technician_detail = EmployeeMiniSerializer(source='technician', read_only=True)

    class Meta:
        model = MaintenanceTicket
        fields = [
            'id', 'asset', 'asset_tag', 'asset_name', 'reported_by', 'reported_by_detail',
            'technician', 'technician_detail', 'issue', 'notes', 'priority', 'status',
            'created_at', 'resolved_at',
        ]
        read_only_fields = ['id', 'status', 'reported_by', 'created_at', 'resolved_at']


class MoveCardSerializer(serializers.Serializer):
    """Body for the kanban drag-and-drop endpoint."""
    status = serializers.ChoiceField(choices=MaintenanceTicket.Status.choices)
    technician = serializers.IntegerField(required=False, allow_null=True)

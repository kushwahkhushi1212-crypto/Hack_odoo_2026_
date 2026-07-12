from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts.permissions import IsOrgAdmin
from assets.models import Asset, AssetUsageEvent
from notifications.services import notify
from .models import MaintenanceStatusLog, MaintenanceTicket
from .serializers import MaintenanceTicketSerializer, MoveCardSerializer

User = get_user_model()

# Only these forward/backward moves are allowed on the kanban board.
VALID_TRANSITIONS = {
    MaintenanceTicket.Status.PENDING: {MaintenanceTicket.Status.APPROVED},
    MaintenanceTicket.Status.APPROVED: {MaintenanceTicket.Status.ASSIGNED, MaintenanceTicket.Status.PENDING},
    MaintenanceTicket.Status.ASSIGNED: {MaintenanceTicket.Status.IN_PROGRESS, MaintenanceTicket.Status.APPROVED},
    MaintenanceTicket.Status.IN_PROGRESS: {MaintenanceTicket.Status.RESOLVED, MaintenanceTicket.Status.ASSIGNED},
    MaintenanceTicket.Status.RESOLVED: set(),
}


class MaintenanceTicketViewSet(viewsets.ModelViewSet):
    """
    Maintenance Management screen. Any employee can raise a ticket
    (status starts PENDING); moving cards across the kanban columns is
    an admin action that also keeps the linked Asset's status in sync.
    """
    queryset = MaintenanceTicket.objects.select_related('asset', 'reported_by', 'technician').all()
    serializer_class = MaintenanceTicketSerializer
    filterset_fields = ['status', 'asset', 'technician', 'priority']

    def get_permissions(self):
        if self.action == 'move':
            return [IsOrgAdmin()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(reported_by=self.request.user)

    @action(detail=False, methods=['get'])
    def board(self, request):
        """GET /api/maintenance/tickets/board/ — tickets grouped by kanban column."""
        data = {}
        for status_value, _ in MaintenanceTicket.Status.choices:
            tickets = self.get_queryset().filter(status=status_value)
            data[status_value] = MaintenanceTicketSerializer(tickets, many=True).data
        return Response(data)

    @action(detail=True, methods=['post'])
    def move(self, request, pk=None):
        """
        POST /api/maintenance/tickets/<id>/move/  {"status": "assigned", "technician": 4}
        Backs dragging a card to a new kanban column.
        """
        ticket = self.get_object()
        serializer = MoveCardSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_status = serializer.validated_data['status']

        allowed = VALID_TRANSITIONS.get(ticket.status, set())
        if new_status not in allowed and new_status != ticket.status:
            return Response(
                {'detail': f"Cannot move a '{ticket.status}' card directly to '{new_status}'."},
                status=400,
            )

        old_status = ticket.status
        ticket.status = new_status

        technician_id = serializer.validated_data.get('technician')
        if technician_id:
            ticket.technician = User.objects.filter(pk=technician_id).first()

        if new_status == MaintenanceTicket.Status.APPROVED:
            ticket.asset.status = Asset.Status.MAINTENANCE
            ticket.asset.save(update_fields=['status', 'updated_at'])
        elif new_status == MaintenanceTicket.Status.RESOLVED:
            ticket.resolved_at = timezone.now()
            ticket.asset.status = Asset.Status.AVAILABLE
            ticket.asset.save(update_fields=['status', 'updated_at'])
            AssetUsageEvent.objects.create(asset=ticket.asset, source='maintenance')

        ticket.save()
        MaintenanceStatusLog.objects.create(
            ticket=ticket, from_status=old_status, to_status=new_status, changed_by=request.user,
        )

        notify(
            recipients=[ticket.reported_by],
            category='alert' if new_status == MaintenanceTicket.Status.RESOLVED else 'approval',
            message=f"Maintenance {ticket.asset.tag}: moved to '{ticket.get_status_display()}'",
            related_object=ticket,
        )
        return Response(MaintenanceTicketSerializer(ticket).data)

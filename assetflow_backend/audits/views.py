from django.utils import timezone
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts.permissions import IsOrgAdmin
from notifications.services import notify
from .models import AuditCycle, AuditItem
from .serializers import AuditCycleSerializer, AuditItemSerializer


class AuditCycleViewSet(viewsets.ModelViewSet):
    """Asset Audit screen — one cycle per department per period. Admin only to create/close."""
    queryset = AuditCycle.objects.select_related('department').prefetch_related('auditors').all()
    serializer_class = AuditCycleSerializer
    permission_classes = [IsOrgAdmin]
    filterset_fields = ['department', 'status']

    @action(detail=True, methods=['get'], url_path='discrepancy-report')
    def discrepancy_report(self, request, pk=None):
        """GET /api/audits/cycles/<id>/discrepancy-report/ — the amber banner's "View report"."""
        cycle = self.get_object()
        items = cycle.items.filter(
            verification__in=[AuditItem.Verification.MISSING, AuditItem.Verification.DAMAGED]
        ).select_related('asset')
        return Response(AuditItemSerializer(items, many=True).data)

    @action(detail=True, methods=['post'], url_path='close')
    def close_cycle(self, request, pk=None):
        """POST /api/audits/cycles/<id>/close/ — "Close audit cycle" button."""
        cycle = self.get_object()
        if cycle.status == AuditCycle.Status.CLOSED:
            return Response({'detail': 'Cycle already closed.'}, status=400)
        if cycle.items.filter(verification=AuditItem.Verification.PENDING).exists():
            return Response({'detail': 'All assets must be verified before closing.'}, status=400)

        cycle.status = AuditCycle.Status.CLOSED
        cycle.closed_at = timezone.now()
        cycle.save(update_fields=['status', 'closed_at'])

        discrepancies = cycle.items.filter(
            verification__in=[AuditItem.Verification.MISSING, AuditItem.Verification.DAMAGED]
        ).count()
        if discrepancies:
            notify(
                recipients=list(cycle.auditors.all()),
                category='alert',
                message=f"Audit '{cycle.name}' closed with {discrepancies} discrepancy(ies) flagged",
                related_object=cycle,
            )
        return Response(AuditCycleSerializer(cycle).data)


class AuditItemViewSet(viewsets.ModelViewSet):
    """Rows of the audit table. Verifying a row is open to any authenticated auditor."""
    queryset = AuditItem.objects.select_related('asset', 'cycle').all()
    serializer_class = AuditItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['cycle', 'verification']

    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """POST /api/audits/items/<id>/verify/ {"verification": "missing", "notes": "..."}"""
        item = self.get_object()
        verification = request.data.get('verification')
        if verification not in AuditItem.Verification.values:
            return Response({'detail': 'Invalid verification value.'}, status=400)

        item.verification = verification
        item.notes = request.data.get('notes', item.notes)
        item.verified_by = request.user
        item.verified_at = timezone.now()
        item.save(update_fields=['verification', 'notes', 'verified_by', 'verified_at'])
        return Response(AuditItemSerializer(item).data)

from django.db import transaction
from django.utils import timezone
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts.permissions import IsOrgAdmin
from assets.models import AllocationHistory, Asset, AssetUsageEvent
from notifications.services import notify
from .models import TransferRequest
from .serializers import TransferDecisionSerializer, TransferRequestSerializer


class TransferRequestViewSet(viewsets.ModelViewSet):
    """
    Allocation & Transfer screen. Any employee can submit a request; only
    admins can approve/reject. Approving is the only path that actually
    moves an asset's `current_holder`.
    """
    queryset = TransferRequest.objects.select_related(
        'asset', 'from_employee', 'to_employee', 'requested_by'
    ).all()
    serializer_class = TransferRequestSerializer
    filterset_fields = ['status', 'asset', 'to_employee']

    def get_permissions(self):
        if self.action in ('approve', 'reject', 'destroy'):
            return [IsOrgAdmin()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(requested_by=self.request.user)
        transfer = serializer.instance
        notify(
            recipients=[u for u in {transfer.to_employee} if u],
            category='approval',
            message=f"Transfer requested: {transfer.asset.tag} to {transfer.to_employee.get_full_name()}",
            related_object=transfer,
        )

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """POST /api/transfers/requests/<id>/approve/"""
        transfer = self.get_object()
        if transfer.status != TransferRequest.Status.PENDING:
            return Response({'detail': 'Only pending requests can be approved.'}, status=400)

        serializer = TransferDecisionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            asset = Asset.objects.select_for_update().get(pk=transfer.asset_id)

            if transfer.from_employee:
                AllocationHistory.objects.create(
                    asset=asset, employee=transfer.from_employee, department=asset.department,
                    action=AllocationHistory.Action.RETURNED,
                    notes=serializer.validated_data.get('notes', ''),
                )

            asset.current_holder = transfer.to_employee
            asset.department = transfer.to_employee.department
            asset.status = Asset.Status.ALLOCATED
            asset.save(update_fields=['current_holder', 'department', 'status', 'updated_at'])

            AllocationHistory.objects.create(
                asset=asset, employee=transfer.to_employee, department=asset.department,
                action=AllocationHistory.Action.ALLOCATED,
                notes=serializer.validated_data.get('notes', ''),
            )
            AssetUsageEvent.objects.create(asset=asset, source='transfer')

            transfer.status = TransferRequest.Status.APPROVED
            transfer.resolved_by = request.user
            transfer.resolved_at = timezone.now()
            transfer.save(update_fields=['status', 'resolved_by', 'resolved_at'])

        notify(
            recipients=[transfer.to_employee, transfer.requested_by],
            category='approval',
            message=f"Transfer approved — {asset.tag} to {transfer.to_employee.get_full_name()}",
            related_object=transfer,
        )
        return Response(TransferRequestSerializer(transfer).data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """POST /api/transfers/requests/<id>/reject/"""
        transfer = self.get_object()
        if transfer.status != TransferRequest.Status.PENDING:
            return Response({'detail': 'Only pending requests can be rejected.'}, status=400)

        transfer.status = TransferRequest.Status.REJECTED
        transfer.resolved_by = request.user
        transfer.resolved_at = timezone.now()
        transfer.save(update_fields=['status', 'resolved_by', 'resolved_at'])

        notify(
            recipients=[transfer.requested_by],
            category='approval',
            message=f"Transfer request rejected — {transfer.asset.tag}",
            related_object=transfer,
        )
        return Response(TransferRequestSerializer(transfer).data)

from datetime import timedelta

from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from assets.models import Asset, AssetUsageEvent
from bookings.models import Booking
from maintenance.models import MaintenanceTicket
from organization.models import Department
from transfers.models import TransferRequest


class DashboardView(APIView):
    """
    GET /api/reports/dashboard/ — powers every stat-card on the Dashboard
    screen (available / allocated / under-maintenance, active bookings,
    pending transfers, upcoming returns).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        now = timezone.now()
        assets = Asset.objects.all()

        return Response({
            'available': assets.filter(status=Asset.Status.AVAILABLE).count(),
            'allocated': assets.filter(status=Asset.Status.ALLOCATED).count(),
            'under_maintenance': assets.filter(status=Asset.Status.MAINTENANCE).count(),
            'active_bookings': Booking.objects.filter(
                status=Booking.Status.CONFIRMED, end_time__gte=now,
            ).count(),
            'pending_transfers': TransferRequest.objects.filter(
                status=TransferRequest.Status.PENDING,
            ).count(),
            'upcoming_returns': MaintenanceTicket.objects.filter(
                status__in=[MaintenanceTicket.Status.APPROVED, MaintenanceTicket.Status.ASSIGNED,
                            MaintenanceTicket.Status.IN_PROGRESS],
            ).count(),
        })


class UtilizationByDepartmentView(APIView):
    """GET /api/reports/utilization/ — bar chart of allocated-asset share per department."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = []
        for dept in Department.objects.filter(is_active=True):
            total = Asset.objects.filter(department=dept).count()
            allocated = Asset.objects.filter(department=dept, status=Asset.Status.ALLOCATED).count()
            utilization = round((allocated / total) * 100, 1) if total else 0
            data.append({'department': dept.name, 'total_assets': total,
                         'allocated': allocated, 'utilization_pct': utilization})
        return Response(data)


class MaintenanceFrequencyView(APIView):
    """GET /api/reports/maintenance-frequency/?months=6 — line chart of tickets raised per month."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        months = int(request.query_params.get('months', 6))
        since = timezone.now() - timedelta(days=30 * months)
        qs = (
            MaintenanceTicket.objects.filter(created_at__gte=since)
            .annotate(month=TruncMonth('created_at'))
            .values('month')
            .annotate(count=Count('id'))
            .order_by('month')
        )
        return Response(list(qs))


class MostUsedAssetsView(APIView):
    """GET /api/reports/most-used/?limit=5 — most-used assets/resources list."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        limit = int(request.query_params.get('limit', 5))
        qs = (
            AssetUsageEvent.objects.values('asset__tag', 'asset__name')
            .annotate(uses=Count('id'))
            .order_by('-uses')[:limit]
        )
        rooms = (
            Booking.objects.filter(status=Booking.Status.CONFIRMED)
            .values('resource__name')
            .annotate(bookings=Count('id'))
            .order_by('-bookings')[:limit]
        )
        return Response({'assets': list(qs), 'resources': list(rooms)})


class IdleAssetsView(APIView):
    """GET /api/reports/idle/?days=30 — idle-assets-due-for-retirement list."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        days = int(request.query_params.get('days', 30))
        cutoff = timezone.now() - timedelta(days=days)

        recently_used_ids = AssetUsageEvent.objects.filter(
            occurred_at__gte=cutoff
        ).values_list('asset_id', flat=True)

        idle = (
            Asset.objects.exclude(id__in=recently_used_ids)
            .exclude(status=Asset.Status.RETIRED)
            .filter(created_at__lt=cutoff)
        )
        return Response([
            {
                'tag': a.tag, 'name': a.name, 'status': a.status,
                'days_since_created': (timezone.now() - a.created_at).days,
            }
            for a in idle
        ])

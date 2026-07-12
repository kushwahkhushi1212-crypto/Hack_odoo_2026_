from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts.permissions import IsOrgAdminOrReadOnly
from assets.models import AssetUsageEvent
from notifications.services import notify
from .models import BookableResource, Booking
from .serializers import BookableResourceSerializer, BookingSerializer


class BookableResourceViewSet(viewsets.ModelViewSet):
    """Resource picklist ("Conference room B2 …") on the Resource Booking screen."""
    queryset = BookableResource.objects.all()
    serializer_class = BookableResourceSerializer
    permission_classes = [IsOrgAdminOrReadOnly]
    filterset_fields = ['is_active']
    search_fields = ['name', 'location']


class BookingViewSet(viewsets.ModelViewSet):
    """
    Booking calendar. A request that overlaps an existing CONFIRMED booking
    on the same resource is never silently double-booked — it is stored as
    CONFLICT for manual resolution, mirroring the dashed "conflict" slot
    in the UI.
    """
    queryset = Booking.objects.select_related('resource', 'booked_by').all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['resource', 'status', 'booked_by']
    ordering_fields = ['start_time']

    def perform_create(self, serializer):
        resource = serializer.validated_data['resource']
        start = serializer.validated_data['start_time']
        end = serializer.validated_data['end_time']

        clashing = Booking.objects.filter(
            resource=resource, status=Booking.Status.CONFIRMED,
            start_time__lt=end, end_time__gt=start,
        ).exists()

        status = Booking.Status.CONFLICT if clashing else Booking.Status.CONFIRMED
        booking = serializer.save(booked_by=self.request.user, status=status)

        if status == Booking.Status.CONFIRMED:
            AssetUsageEvent.objects.create(asset=resource.asset, source='booking') if resource.asset_id else None
        notify(
            recipients=[self.request.user],
            category='booking',
            message=(
                f"Booking confirmed — {resource.name}, {start:%H:%M}–{end:%H:%M}"
                if status == Booking.Status.CONFIRMED else
                f"Booking conflict — {resource.name}, {start:%H:%M}–{end:%H:%M} is already held"
            ),
            related_object=booking,
        )

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """POST /api/bookings/bookings/<id>/cancel/"""
        booking = self.get_object()
        booking.status = Booking.Status.CANCELLED
        booking.save(update_fields=['status'])
        return Response(BookingSerializer(booking).data)

    @action(detail=False, methods=['get'])
    def week(self, request):
        """GET /api/bookings/bookings/week/?resource=<id>&start=YYYY-MM-DD — "This week" summary card."""
        from datetime import timedelta
        from django.utils.dateparse import parse_date

        resource_id = request.query_params.get('resource')
        start_str = request.query_params.get('start')
        start_date = parse_date(start_str) if start_str else None
        if not start_date:
            from django.utils import timezone
            start_date = timezone.localdate() - timedelta(days=timezone.localdate().weekday())

        qs = self.get_queryset().filter(
            start_time__date__gte=start_date, start_time__date__lt=start_date + timedelta(days=7),
        )
        if resource_id:
            qs = qs.filter(resource_id=resource_id)

        days = []
        for i in range(5):  # Mon–Fri, matching the UI
            day = start_date + timedelta(days=i)
            day_qs = qs.filter(start_time__date=day)
            days.append({
                'date': day,
                'bookings': day_qs.filter(status=Booking.Status.CONFIRMED).count(),
                'conflicts': day_qs.filter(status=Booking.Status.CONFLICT).count(),
            })
        return Response(days)

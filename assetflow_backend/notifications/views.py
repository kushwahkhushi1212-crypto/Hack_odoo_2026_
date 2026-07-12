from rest_framework import mixins, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Notification
from .serializers import NotificationSerializer


class NotificationViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    Notifications / Activity Log screen. Every user only ever sees their
    own notifications; the "All / Alerts / Approvals / Bookings" chips map
    straight to ?category=.
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['category', 'is_read']

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)

    @action(detail=True, methods=['post'])
    def read(self, request, pk=None):
        """POST /api/notifications/notifications/<id>/read/"""
        notification = self.get_object()
        notification.is_read = True
        notification.save(update_fields=['is_read'])
        return Response(NotificationSerializer(notification).data)

    @action(detail=False, methods=['post'], url_path='read-all')
    def read_all(self, request):
        """POST /api/notifications/notifications/read-all/"""
        self.get_queryset().update(is_read=True)
        return Response({'detail': 'All notifications marked read.'})

    @action(detail=False, methods=['get'], url_path='unread-count')
    def unread_count(self, request):
        """GET /api/notifications/notifications/unread-count/ — powers the bell's red dot."""
        return Response({'unread': self.get_queryset().filter(is_read=False).count()})

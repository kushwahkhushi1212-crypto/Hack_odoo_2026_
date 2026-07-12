from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts.permissions import IsOrgAdmin
from .filters import AssetFilter
from .models import AllocationHistory, Asset
from .serializers import AllocationHistorySerializer, AssetSerializer


class AssetViewSet(viewsets.ModelViewSet):
    """
    Asset Directory screen: search, category/status/department chip filters,
    "Register asset", and a per-asset allocation-history sub-resource.
    """
    queryset = Asset.objects.select_related('category', 'department', 'current_holder').all()
    serializer_class = AssetSerializer
    filterset_class = AssetFilter
    search_fields = ['tag', 'name', 'qr_code']
    ordering_fields = ['created_at', 'name', 'status']

    def get_permissions(self):
        # Anyone signed in can register/browse assets; only admins can
        # edit or delete an existing record directly.
        if self.action in ('update', 'partial_update', 'destroy'):
            return [IsOrgAdmin()]
        return [permissions.IsAuthenticated()]

    @action(detail=True, methods=['get'], url_path='history')
    def history(self, request, pk=None):
        """GET /api/assets/assets/<id>/history/ — allocation history panel."""
        asset = self.get_object()
        qs = asset.history.select_related('employee', 'department').all()
        return Response(AllocationHistorySerializer(qs, many=True).data)

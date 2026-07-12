from rest_framework import viewsets

from accounts.permissions import IsOrgAdminOrReadOnly
from .models import Category, Department
from .serializers import CategorySerializer, DepartmentSerializer


class DepartmentViewSet(viewsets.ModelViewSet):
    """
    Departments tab of Organization Setup. Editing here also updates the
    picklist used by Assets and Reports, since both simply FK this model.
    """
    queryset = Department.objects.select_related('head', 'parent').all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsOrgAdminOrReadOnly]
    filterset_fields = ['is_active', 'parent']
    search_fields = ['name', 'code']


class CategoryViewSet(viewsets.ModelViewSet):
    """Categories tab of Organization Setup."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsOrgAdminOrReadOnly]
    filterset_fields = ['is_active']
    search_fields = ['name']

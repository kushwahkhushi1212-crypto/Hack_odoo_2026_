from django.urls import path

from .views import (
    DashboardView, IdleAssetsView, MaintenanceFrequencyView,
    MostUsedAssetsView, UtilizationByDepartmentView,
)

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='report-dashboard'),
    path('utilization/', UtilizationByDepartmentView.as_view(), name='report-utilization'),
    path('maintenance-frequency/', MaintenanceFrequencyView.as_view(), name='report-maintenance-frequency'),
    path('most-used/', MostUsedAssetsView.as_view(), name='report-most-used'),
    path('idle/', IdleAssetsView.as_view(), name='report-idle'),
]

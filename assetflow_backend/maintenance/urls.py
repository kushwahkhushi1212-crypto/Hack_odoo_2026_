from rest_framework.routers import DefaultRouter

from .views import MaintenanceTicketViewSet

router = DefaultRouter()
router.register('tickets', MaintenanceTicketViewSet, basename='maintenance-ticket')

urlpatterns = router.urls

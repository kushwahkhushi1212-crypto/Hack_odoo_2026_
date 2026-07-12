from rest_framework.routers import DefaultRouter

from .views import AuditCycleViewSet, AuditItemViewSet

router = DefaultRouter()
router.register('cycles', AuditCycleViewSet, basename='audit-cycle')
router.register('items', AuditItemViewSet, basename='audit-item')

urlpatterns = router.urls

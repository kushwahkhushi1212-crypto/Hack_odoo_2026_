from rest_framework.routers import DefaultRouter

from .views import TransferRequestViewSet

router = DefaultRouter()
router.register('requests', TransferRequestViewSet, basename='transfer-request')

urlpatterns = router.urls

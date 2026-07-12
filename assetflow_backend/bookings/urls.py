from rest_framework.routers import DefaultRouter

from .views import BookableResourceViewSet, BookingViewSet

router = DefaultRouter()
router.register('resources', BookableResourceViewSet, basename='resource')
router.register('bookings', BookingViewSet, basename='booking')

urlpatterns = router.urls

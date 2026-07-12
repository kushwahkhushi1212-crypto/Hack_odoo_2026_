from rest_framework.routers import DefaultRouter

from .views import CategoryViewSet, DepartmentViewSet

router = DefaultRouter()
router.register('departments', DepartmentViewSet, basename='department')
router.register('categories', CategoryViewSet, basename='category')

urlpatterns = router.urls

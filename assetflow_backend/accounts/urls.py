from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import ChangeRoleView, EmployeeViewSet, MeView, SignupView

router = DefaultRouter()
router.register('employees', EmployeeViewSet, basename='employee')

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('me/', MeView.as_view(), name='me'),
    path('employees/<int:pk>/role/', ChangeRoleView.as_view(), name='employee-change-role'),
] + router.urls

"""
AssetFlow root URL configuration.
All feature APIs are namespaced under /api/.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenRefreshView
from accounts.views import LoginView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Auth
    path('api/auth/login/', LoginView.as_view(), name='login'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/', include('accounts.urls')),

    # Feature apps
    path('api/org/', include('organization.urls')),
    path('api/assets/', include('assets.urls')),
    path('api/transfers/', include('transfers.urls')),
    path('api/bookings/', include('bookings.urls')),
    path('api/maintenance/', include('maintenance.urls')),
    path('api/audits/', include('audits.urls')),
    path('api/notifications/', include('notifications.urls')),
    path('api/reports/', include('reports.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

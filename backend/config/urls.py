from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
import settings



urlpatterns = [
    path('admin/', admin.site.urls),

    # API endpoints
    path('api/auth/', include('apps.accounts.urls')),
    path('api/projects', include('apps.projects.urls')),
    path('api/api-keys', include('apps.api_keys.urls')),
    path('api/api-logs/', include('apps.api_logs.urls')),
    path('api/rate-limiting/', include('apps.rate_limiting.urls')),
    path('api/gateway/', include('apps.gateway.urls')),     # Internal management
    path('', include('apps.gateway.urls')),     # External API endpoints
    
    # OpenAPI documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

# Debug toolbar
try:
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns += [
            path('__debug__/', include(debug_toolbar.urls)),
        ]
except ImportError:
    pass        
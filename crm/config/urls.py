from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from drf_spectacular.views import (
    SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView,
)

api_v1 = [
    path('auth/', include('apps.auth_app.urls')),
    path('customers/', include('apps.customers.urls')),
    path('segments/', include('apps.segments.urls')),
    path('campaigns/', include('apps.campaigns.urls')),
    path('campaign-templates/', include(('apps.campaigns.urls_templates', 'campaign_templates'))),
    path('communication-logs/', include(('apps.campaigns.urls_logs', 'communication_logs'))),
    path('analytics/', include('apps.analytics.urls')),
    path('copilot/', include('apps.copilot.urls')),
    path('webhooks/', include('apps.webhooks.urls')),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include((api_v1, 'api_v1'))),

    # OpenAPI schema + UIs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('docs/', RedirectView.as_view(pattern_name='swagger-ui', permanent=False)),
]

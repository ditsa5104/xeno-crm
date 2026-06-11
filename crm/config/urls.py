from django.contrib import admin
from django.urls import path, include

api_v1 = [
    path('customers/', include('apps.customers.urls')),
    path('segments/', include('apps.segments.urls')),
    path('campaigns/', include('apps.campaigns.urls')),
    path('campaign-templates/', include(('apps.campaigns.urls_templates', 'campaign_templates'))),
    path('analytics/', include('apps.analytics.urls')),
    path('copilot/', include('apps.copilot.urls')),
    path('webhooks/', include('apps.webhooks.urls')),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include((api_v1, 'api_v1'))),
]

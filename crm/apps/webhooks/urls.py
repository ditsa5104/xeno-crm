from django.urls import path
from .views import ChannelEventWebhookView

urlpatterns = [
    path('channel-event/', ChannelEventWebhookView.as_view(), name='channel-event'),
]

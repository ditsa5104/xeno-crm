from django.urls import path
from .views import DashboardView, CohortsView, ChannelsView

urlpatterns = [
    path('dashboard/', DashboardView.as_view()),
    path('cohorts/', CohortsView.as_view()),
    path('channels/', ChannelsView.as_view()),
]

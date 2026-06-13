from django.urls import path
from .views import (
    DashboardView, OverviewView, CohortsView, ChannelsView,
    InsightView, InsightCatalogueView,
)

urlpatterns = [
    path('dashboard/', DashboardView.as_view()),
    path('overview/', OverviewView.as_view()),
    path('cohorts/', CohortsView.as_view()),
    path('channels/', ChannelsView.as_view()),
    path('insights/', InsightCatalogueView.as_view()),
    path('insights/<str:key>/', InsightView.as_view()),
]

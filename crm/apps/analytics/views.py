from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from drf_spectacular.utils import extend_schema, OpenApiResponse
from . import aggregators


@extend_schema(
    tags=['analytics'],
    summary='Dashboard summary',
    description='Top-line counts and overall delivery rate.',
    responses={200: OpenApiResponse(description='Aggregate counts and delivery rate.')},
)
class DashboardView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        return Response(aggregators.dashboard_summary())


@extend_schema(
    tags=['analytics'],
    summary='Dashboard overview',
    description='Bundled dashboard payload: summary metrics, recent campaigns, '
                'top segments, and a 30-day performance time series.',
    responses={200: OpenApiResponse(description='Composite dashboard payload.')},
)
class OverviewView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        return Response({
            'summary': aggregators.dashboard_summary(),
            'recent_campaigns': aggregators.recent_campaigns(),
            'top_segments': aggregators.top_segments(),
            'performance': aggregators.performance_timeseries(),
        })


@extend_schema(
    tags=['analytics'],
    summary='Cohort analysis',
    description='Customers and spend grouped by acquisition month.',
    responses={200: OpenApiResponse(description='List of {month, customers, spend}.')},
)
class CohortsView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        return Response(aggregators.cohort_analysis())


@extend_schema(
    tags=['analytics'],
    summary='Channel performance',
    description='Per-channel breakdown of total/delivered/opened/clicked/failed plus rates.',
    responses={200: OpenApiResponse(description='List of channel stats.')},
)
class ChannelsView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        return Response(aggregators.channel_performance())

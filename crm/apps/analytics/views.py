from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from drf_spectacular.utils import extend_schema, OpenApiResponse
from . import aggregators
from . import insights as insights_mod


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


import json
import logging
from openai import APIError, RateLimitError
from apps.core.ai_client import get_ai_client, get_model
from apps.copilot.prompts import INSIGHT_PLAYBOOK_SYSTEM_PROMPT

_logger = logging.getLogger(__name__)


def _generate_playbook(insight):
    """Turn a structured insight into a short NL playbook. Degrades gracefully:
    if the AI is unavailable, returns None and the data recommendation stands."""
    sample = [
        {k: c[k] for k in ('name', 'rfm_tier', 'churn_risk_score', 'total_spend', 'channel_preference')}
        for c in insight.get('customers', [])[:8]
    ]
    if not sample:
        return None
    user_msg = json.dumps({'insight': insight.get('title'), 'customers': sample}, default=str)
    try:
        client = get_ai_client()
        resp = client.chat.completions.create(
            model=get_model(),
            max_tokens=320,
            messages=[
                {'role': 'system', 'content': INSIGHT_PLAYBOOK_SYSTEM_PROMPT},
                {'role': 'user', 'content': user_msg},
            ],
        )
        return resp.choices[0].message.content.strip()
    except (APIError, RateLimitError) as e:
        _logger.warning("Insight playbook AI failed: %s", e)
        return None


@extend_schema(
    tags=['analytics'],
    summary='AI action insight',
    description=(
        'Powers the contextual "do this now" buttons. Returns a data-grounded list of '
        'recommended customers for a named insight plus an optional AI playbook. '
        'Valid keys: who_to_contact_today, win_back, reward_vips, grow_rising.'
    ),
    responses={200: OpenApiResponse(description='Insight payload with customers and playbook.')},
)
class InsightView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, key):
        fn = insights_mod.INSIGHT_FUNCS.get(key)
        if not fn:
            return Response({'error': f'Unknown insight "{key}"'}, status=400)
        try:
            limit = max(1, min(int(request.query_params.get('limit', 10)), 50))
        except (TypeError, ValueError):
            limit = 10
        insight = fn(limit=limit)
        # AI playbook is opt-out via ?playbook=0 to keep the call fast when not needed.
        if request.query_params.get('playbook', '1') != '0':
            insight['playbook'] = _generate_playbook(insight)
        return Response(insight)


@extend_schema(
    tags=['analytics'],
    summary='List available AI action insights',
    responses={200: OpenApiResponse(description='Insight catalogue.')},
)
class InsightCatalogueView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    CATALOGUE = [
        {'key': 'who_to_contact_today', 'label': 'Who do I talk to today?', 'icon': 'phone'},
        {'key': 'win_back', 'label': 'Win back lapsed customers', 'icon': 'undo'},
        {'key': 'reward_vips', 'label': 'Reward my VIPs', 'icon': 'crown'},
        {'key': 'grow_rising', 'label': 'Grow rising customers', 'icon': 'trending-up'},
    ]

    def get(self, request):
        return Response({'insights': self.CATALOGUE, 'best_send_window': insights_mod.best_send_window()})

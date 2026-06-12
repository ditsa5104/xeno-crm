import logging
from datetime import timedelta
from decimal import Decimal
from django.db.models import Count, Q, Sum
from django.utils import timezone
from openai import APIError, RateLimitError
from apps.core.ai_client import get_ai_client, get_model
from apps.customers.models import Customer
from apps.segments.models import Segment
from apps.segments.evaluator import SegmentEvaluator
from apps.segments.ai_segmenter import nl_to_filter_tree, SegmenterError
from apps.campaigns.models import Campaign, CommunicationLog
from .prompts import MESSAGE_DRAFTER_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


COPILOT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_campaign_stats",
            "description": "Get performance stats for a specific campaign by name (partial match) or UUID.",
            "parameters": {
                "type": "object",
                "properties": {"campaign_identifier": {"type": "string"}},
                "required": ["campaign_identifier"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "count_customers_by_filter",
            "description": "Count customers matching a natural-language description.",
            "parameters": {
                "type": "object",
                "properties": {"description": {"type": "string"}},
                "required": ["description"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_top_campaigns",
            "description": "List top N campaigns ranked by metric over the last period_days.",
            "parameters": {
                "type": "object",
                "properties": {
                    "metric": {"type": "string", "enum": ["click_rate", "delivery_rate", "conversion_rate", "revenue_attributed", "open_rate"]},
                    "n": {"type": "integer", "default": 5},
                    "period_days": {"type": "integer", "default": 30},
                },
                "required": ["metric"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_top_customers",
            "description": "List the top N customers ranked by a metric such as total spend, total orders, or LTV estimate. Use this to answer questions like 'show me my top customers by spend'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "metric": {"type": "string", "enum": ["total_spend", "total_orders", "ltv_estimate"], "default": "total_spend"},
                    "n": {"type": "integer", "default": 10},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_channel_performance",
            "description": "Aggregated metrics broken down by channel.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_dashboard_summary",
            "description": "High-level CRM summary: customers, segments, campaigns, delivery rate.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_segment_draft",
            "description": "Create a segment from a natural-language filter description.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "nl_filter": {"type": "string"},
                },
                "required": ["name", "nl_filter"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "draft_campaign_messages",
            "description": "Generate 2-3 message variants for a campaign.",
            "parameters": {
                "type": "object",
                "properties": {
                    "audience_description": {"type": "string"},
                    "campaign_goal": {"type": "string"},
                    "tone": {"type": "string", "enum": ["friendly", "urgent", "exclusive", "informative"]},
                    "channel": {"type": "string", "enum": ["whatsapp", "sms", "email", "rcs"]},
                    "n_variants": {"type": "integer", "default": 2},
                },
                "required": ["audience_description", "campaign_goal", "channel"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_campaign_draft",
            "description": "Create a campaign in DRAFT status. Does not launch.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "segment_id": {"type": "string"},
                    "channel": {"type": "string", "enum": ["whatsapp", "sms", "email", "rcs", "auto"]},
                    "message_template": {"type": "string"},
                    "send_mode": {"type": "string", "enum": ["immediate", "scheduled"]},
                    "scheduled_at": {"type": "string"},
                },
                "required": ["name", "segment_id", "channel", "message_template"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_customer_summary",
            "description": "Summary of a customer: profile, orders, campaign history, RFM, churn.",
            "parameters": {
                "type": "object",
                "properties": {"customer_identifier": {"type": "string"}},
                "required": ["customer_identifier"],
            },
        },
    },
]


def _resolve_campaign(identifier):
    qs = Campaign.objects.all()
    try:
        return qs.get(id=identifier)
    except (Campaign.DoesNotExist, ValueError):
        return qs.filter(name__icontains=identifier).first()


def _resolve_customer(identifier):
    return (
        Customer.objects.filter(id=identifier).first()
        or Customer.objects.filter(email__iexact=identifier).first()
        or Customer.objects.filter(phone=identifier).first()
        or Customer.objects.filter(name__icontains=identifier).first()
    )


def get_campaign_stats(campaign_identifier, **_):
    c = _resolve_campaign(campaign_identifier)
    if not c:
        return {'error': f'Campaign "{campaign_identifier}" not found'}
    return {
        'id': str(c.id),
        'name': c.name,
        'status': c.status,
        'channel': c.channel,
        'total': c.stat_total,
        'sent': c.stat_sent,
        'delivered': c.stat_delivered,
        'failed': c.stat_failed,
        'opened': c.stat_opened,
        'clicked': c.stat_clicked,
        'converted': c.stat_converted,
        'revenue_attributed': str(c.stat_revenue_attributed),
        'delivery_rate': c.stat_delivered / c.stat_total if c.stat_total else 0,
        'click_rate': c.stat_clicked / c.stat_delivered if c.stat_delivered else 0,
    }


def count_customers_by_filter(description, **_):
    try:
        tree = nl_to_filter_tree(description)
    except SegmenterError as e:
        return {'error': str(e)}
    try:
        qs = SegmentEvaluator().evaluate(tree)
        return {'count': qs.count(), 'filter_tree': tree}
    except ValueError as e:
        return {'error': str(e), 'filter_tree': tree}


def list_top_campaigns(metric, n=5, period_days=30, **_):
    cutoff = timezone.now() - timedelta(days=period_days)
    qs = Campaign.objects.filter(launched_at__gte=cutoff, stat_total__gt=0)
    out = []
    for c in qs:
        if metric == 'click_rate':
            v = c.stat_clicked / c.stat_delivered if c.stat_delivered else 0
        elif metric == 'delivery_rate':
            v = c.stat_delivered / c.stat_total if c.stat_total else 0
        elif metric == 'conversion_rate':
            v = c.stat_converted / c.stat_delivered if c.stat_delivered else 0
        elif metric == 'open_rate':
            v = c.stat_opened / c.stat_delivered if c.stat_delivered else 0
        else:  # revenue_attributed
            v = float(c.stat_revenue_attributed)
        out.append({'id': str(c.id), 'name': c.name, 'metric': v, 'channel': c.channel})
    out.sort(key=lambda x: -x['metric'])
    return {'campaigns': out[:n], 'metric': metric}


def get_channel_performance(**_):
    from apps.analytics.aggregators import channel_performance
    return {'channels': channel_performance()}


def list_top_customers(metric='total_spend', n=10, **_):
    allowed = {'total_spend', 'total_orders', 'ltv_estimate'}
    if metric not in allowed:
        metric = 'total_spend'
    try:
        n = max(1, min(int(n), 50))
    except (TypeError, ValueError):
        n = 10
    rows = Customer.objects.order_by(f'-{metric}')[:n]
    return {
        'metric': metric,
        'customers': [
            {
                'id': str(c.id),
                'name': c.name,
                'email': c.email,
                'city': c.city,
                'total_spend': float(c.total_spend),
                'total_orders': c.total_orders,
                'ltv_estimate': float(c.ltv_estimate),
                'rfm_tier': c.rfm_tier,
            }
            for c in rows
        ],
    }


def get_dashboard_summary(**_):
    from apps.analytics.aggregators import dashboard_summary
    return dashboard_summary()


def create_segment_draft(name, nl_filter, description='', **_):
    try:
        tree = nl_to_filter_tree(nl_filter)
    except SegmenterError as e:
        return {'error': str(e)}
    seg = Segment.objects.create(
        name=name, description=description, segment_type='dynamic',
        filter_tree=tree, natural_query=nl_filter, ai_generated=True,
    )
    try:
        seg.customer_count = SegmentEvaluator().evaluate(tree).count()
        seg.last_computed = timezone.now()
        seg.save(update_fields=['customer_count', 'last_computed'])
    except ValueError:
        pass
    return {'segment_id': str(seg.id), 'name': seg.name, 'customer_count': seg.customer_count}


def draft_campaign_messages(audience_description, campaign_goal, channel, tone='friendly', n_variants=2, **_):
    client = get_ai_client()
    sys = MESSAGE_DRAFTER_SYSTEM_PROMPT.format(n_variants=n_variants)
    user_msg = (
        f"Audience: {audience_description}\n"
        f"Goal: {campaign_goal}\n"
        f"Channel: {channel}\n"
        f"Tone: {tone}"
    )
    try:
        resp = client.chat.completions.create(
            model=get_model(),
            max_tokens=600,
            messages=[
                {'role': 'system', 'content': sys},
                {'role': 'user', 'content': user_msg},
            ],
        )
        text = resp.choices[0].message.content
    except (APIError, RateLimitError) as e:
        logger.warning("draft_campaign_messages AI failed: %s", e)
        text = f"Variant 1: Hi {{{{name}}}}, exclusive offer for {{{{city}}}} — check it out!\nVariant 2: Hello {{{{name}}}}, we picked something just for you in {{{{city}}}}."
    variants = []
    for line in text.splitlines():
        line = line.strip()
        if line.startswith('Variant'):
            _, _, body = line.partition(':')
            variants.append(body.strip())
    if not variants:
        variants = [text.strip()]
    return {'variants': variants}


def create_campaign_draft(name, segment_id, channel, message_template, send_mode='immediate', scheduled_at=None, **_):
    try:
        seg = Segment.objects.get(id=segment_id)
    except Segment.DoesNotExist:
        return {'error': f'Segment {segment_id} not found'}
    c = Campaign.objects.create(
        name=name, segment=seg, channel=channel, message_template=message_template,
        send_mode=send_mode, status='draft', ai_generated_copy=True,
    )
    return {'campaign_id': str(c.id), 'name': c.name, 'status': c.status}


def get_customer_summary(customer_identifier, **_):
    c = _resolve_customer(customer_identifier)
    if not c:
        return {'error': f'Customer "{customer_identifier}" not found'}
    recent_logs = CommunicationLog.objects.filter(customer=c).order_by('-queued_at')[:5]
    return {
        'id': str(c.id),
        'name': c.name,
        'email': c.email,
        'city': c.city,
        'rfm_tier': c.rfm_tier,
        'churn_risk_score': c.churn_risk_score,
        'total_spend': str(c.total_spend),
        'total_orders': c.total_orders,
        'last_order_at': c.last_order_at.isoformat() if c.last_order_at else None,
        'recent_campaigns': [
            {'campaign': l.campaign.name, 'status': l.status, 'channel': l.channel}
            for l in recent_logs
        ],
    }


TOOL_IMPL = {
    'get_campaign_stats': get_campaign_stats,
    'count_customers_by_filter': count_customers_by_filter,
    'list_top_campaigns': list_top_campaigns,
    'list_top_customers': list_top_customers,
    'get_channel_performance': get_channel_performance,
    'get_dashboard_summary': get_dashboard_summary,
    'create_segment_draft': create_segment_draft,
    'draft_campaign_messages': draft_campaign_messages,
    'create_campaign_draft': create_campaign_draft,
    'get_customer_summary': get_customer_summary,
}

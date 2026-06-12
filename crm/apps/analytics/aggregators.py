from datetime import timedelta
from django.db.models import Count, Sum, F, Q
from django.db.models.functions import TruncMonth
from django.utils import timezone
from apps.customers.models import Customer
from apps.segments.models import Segment
from apps.campaigns.models import Campaign, CommunicationLog


def dashboard_summary():
    now = timezone.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    total_customers = Customer.objects.count()
    active_segments = Segment.objects.filter(customer_count__gt=0).count()
    sent_this_month = CommunicationLog.objects.filter(queued_at__gte=month_start).count()
    delivered = CommunicationLog.objects.filter(status__in=['delivered', 'opened', 'read', 'clicked']).count()
    opened = CommunicationLog.objects.filter(status__in=['opened', 'read', 'clicked']).count()
    clicked = CommunicationLog.objects.filter(status='clicked').count()
    total = CommunicationLog.objects.count()
    rate = (delivered / total) if total else 0
    revenue = Campaign.objects.aggregate(s=Sum('stat_revenue_attributed'))['s'] or 0
    return {
        'total_customers': total_customers,
        'active_segments': active_segments,
        'campaigns_total': Campaign.objects.count(),
        'campaigns_this_month': Campaign.objects.filter(launched_at__gte=month_start).count(),
        'messages_this_month': sent_this_month,
        'messages_delivered': delivered,
        'overall_delivery_rate': round(rate, 4),
        'overall_open_rate': round((opened / delivered) if delivered else 0, 4),
        'overall_click_rate': round((clicked / delivered) if delivered else 0, 4),
        'total_revenue_attributed': float(revenue),
    }


def recent_campaigns(limit=5):
    """Last N campaigns with headline stats for the dashboard table."""
    rows = Campaign.objects.select_related('segment').order_by('-created_at')[:limit]
    out = []
    for c in rows:
        out.append({
            'id': str(c.id),
            'name': c.name,
            'channel': c.channel,
            'segment_name': c.segment.name if c.segment_id else '',
            'status': c.status,
            'sent': c.stat_sent,
            'total': c.stat_total,
            'delivered': c.stat_delivered,
            'opened': c.stat_opened,
            'clicked': c.stat_clicked,
            'open_rate': round((c.stat_opened / c.stat_delivered) if c.stat_delivered else 0, 4),
        })
    return out


def top_segments(limit=5):
    """Segments ranked by engagement (open rate) across their campaigns."""
    rows = (
        Campaign.objects.filter(stat_delivered__gt=0)
        .values('segment__id', 'segment__name')
        .annotate(
            delivered=Sum('stat_delivered'),
            opened=Sum('stat_opened'),
            customers=Sum('segment__customer_count'),
        )
    )
    out = []
    for r in rows:
        if not r['segment__id']:
            continue
        delivered = r['delivered'] or 0
        opened = r['opened'] or 0
        out.append({
            'id': str(r['segment__id']),
            'name': r['segment__name'],
            'engagement_rate': round((opened / delivered) if delivered else 0, 4),
        })
    out.sort(key=lambda x: -x['engagement_rate'])
    return out[:limit]


def performance_timeseries(days=30):
    """Daily sent / opened / clicked counts over the last N days for the chart."""
    now = timezone.now()
    start = (now - timedelta(days=days)).replace(hour=0, minute=0, second=0, microsecond=0)
    buckets = {}
    for i in range(days + 1):
        d = (start + timedelta(days=i)).date().isoformat()
        buckets[d] = {'date': d, 'sent': 0, 'opened': 0, 'clicked': 0}

    logs = CommunicationLog.objects.filter(queued_at__gte=start).values(
        'queued_at', 'opened_at', 'clicked_at'
    )
    for l in logs:
        qd = l['queued_at'].date().isoformat()
        if qd in buckets:
            buckets[qd]['sent'] += 1
        if l['opened_at']:
            od = l['opened_at'].date().isoformat()
            if od in buckets:
                buckets[od]['opened'] += 1
        if l['clicked_at']:
            cd = l['clicked_at'].date().isoformat()
            if cd in buckets:
                buckets[cd]['clicked'] += 1
    return list(buckets.values())


def cohort_analysis():
    """Cohort by acquisition month."""
    rows = (
        Customer.objects
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(
            customers=Count('id'),
            spend=Sum('total_spend'),
        )
        .order_by('month')
    )
    return [
        {'month': r['month'].isoformat() if r['month'] else None, 'customers': r['customers'], 'spend': float(r['spend'] or 0)}
        for r in rows
    ]


def channel_performance():
    rows = (
        CommunicationLog.objects.values('channel').annotate(
            total=Count('id'),
            delivered=Count('id', filter=Q(status__in=['delivered', 'opened', 'read', 'clicked'])),
            opened=Count('id', filter=Q(status__in=['opened', 'read', 'clicked'])),
            clicked=Count('id', filter=Q(status='clicked')),
            failed=Count('id', filter=Q(status='failed')),
        )
    )
    return [
        {
            **r,
            'delivery_rate': r['delivered'] / r['total'] if r['total'] else 0,
            'open_rate': r['opened'] / r['delivered'] if r['delivered'] else 0,
            'click_rate': r['clicked'] / r['delivered'] if r['delivered'] else 0,
        }
        for r in rows
    ]

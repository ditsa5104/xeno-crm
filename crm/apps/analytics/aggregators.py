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
    total = CommunicationLog.objects.count()
    rate = (delivered / total) if total else 0
    return {
        'total_customers': total_customers,
        'active_segments': active_segments,
        'campaigns_this_month': Campaign.objects.filter(launched_at__gte=month_start).count(),
        'messages_this_month': sent_this_month,
        'overall_delivery_rate': round(rate, 4),
    }


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

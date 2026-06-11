import logging
from datetime import timedelta
from decimal import Decimal
from django.utils import timezone
from django.db.models import F
from celery import shared_task
from apps.campaigns.models import CommunicationLog, Campaign
from apps.customers.models import Order

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def run_revenue_attribution(self):
    """
    Attribute orders placed within 7 days after a campaign click/delivery to that campaign.
    """
    now = timezone.now()
    cutoff = now - timedelta(days=14)
    eligible = CommunicationLog.objects.filter(
        delivered_at__gte=cutoff,
        converted=False,
    ).select_related('customer')

    n_attributed = 0
    for log in eligible.iterator():
        anchor = log.clicked_at or log.delivered_at
        if not anchor:
            continue
        order = (
            Order.objects
            .filter(
                customer=log.customer,
                ordered_at__gte=anchor,
                ordered_at__lte=anchor + timedelta(days=7),
            )
            .order_by('ordered_at')
            .first()
        )
        if not order:
            continue
        log.converted = True
        log.conversion_order = order
        log.conversion_at = order.ordered_at
        log.save(update_fields=['converted', 'conversion_order', 'conversion_at'])
        Campaign.objects.filter(id=log.campaign_id).update(
            stat_converted=F('stat_converted') + 1,
            stat_revenue_attributed=F('stat_revenue_attributed') + order.total_amount,
        )
        n_attributed += 1
    logger.info("Attributed %d orders", n_attributed)
    return n_attributed

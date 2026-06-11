import logging
from datetime import timedelta
from django.utils import timezone
from celery import shared_task
from .models import Campaign, CommunicationLog
from .dispatch import CampaignDispatcher

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, queue='campaigns')
def launch_campaign(self, campaign_id):
    try:
        c = Campaign.objects.get(id=campaign_id)
    except Campaign.DoesNotExist:
        return 0
    return CampaignDispatcher(c).dispatch()


@shared_task(bind=True, max_retries=3, queue='campaigns')
def dispatch_single_message(self, log_id):
    """Retry a single failed CommunicationLog by creating a new one."""
    try:
        old = CommunicationLog.objects.get(id=log_id)
    except CommunicationLog.DoesNotExist:
        return None
    new = CommunicationLog.objects.create(
        campaign=old.campaign,
        customer=old.customer,
        channel=old.channel,
        message_body=old.message_body,
        variant_label=old.variant_label,
        retry_count=old.retry_count + 1,
        status='queued',
    )
    CampaignDispatcher(old.campaign)._send_to_stub(new, old.customer)
    return str(new.id)


@shared_task(bind=True, max_retries=3, queue='campaigns')
def select_ab_winners(self):
    """Pick the variant with the highest click rate after sufficient sends."""
    now = timezone.now()
    cutoff = now - timedelta(hours=2)
    qs = Campaign.objects.filter(
        is_ab_test=True, ab_winner_variant='', launched_at__lte=cutoff,
    )
    decided = 0
    for c in qs:
        from django.db.models import Count, Q
        rates = (
            CommunicationLog.objects
            .filter(campaign=c)
            .values('variant_label')
            .annotate(
                sent=Count('id', filter=Q(status__in=['sent', 'delivered', 'opened', 'read', 'clicked'])),
                clicked=Count('id', filter=Q(status='clicked')),
            )
        )
        best = None
        best_rate = -1.0
        for r in rates:
            if r['sent'] < 10:
                continue
            rate = r['clicked'] / r['sent']
            if rate > best_rate:
                best = r['variant_label']
                best_rate = rate
        if best is not None:
            c.ab_winner_variant = best
            c.ab_decided_at = now
            c.save(update_fields=['ab_winner_variant', 'ab_decided_at'])
            decided += 1
    return decided

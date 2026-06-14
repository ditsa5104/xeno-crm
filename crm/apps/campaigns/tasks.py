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


@shared_task(queue='campaigns')
def dispatch_due_campaigns():
    """Beat task: dispatch any scheduled campaign whose send time has arrived.

    Runs frequently (see beat_schedule). A campaign is 'due' when it is in
    'scheduled' status with a scheduled_at in the past. We flip it to 'running'
    inside a row lock first so two overlapping beat ticks can't double-dispatch
    the same campaign.
    """
    from django.db import transaction
    now = timezone.now()
    due = Campaign.objects.filter(
        status='scheduled',
        scheduled_at__isnull=False,
        scheduled_at__lte=now,
    ).values_list('id', flat=True)

    dispatched = 0
    for cid in list(due):
        with transaction.atomic():
            c = Campaign.objects.select_for_update().filter(id=cid, status='scheduled').first()
            if not c:
                continue  # claimed by another tick or status changed
            # Claim it so a concurrent tick won't pick it up. dispatch() will set
            # it to 'running' too, but claiming here closes the race window.
            c.status = 'running'
            c.save(update_fields=['status'])
        launch_campaign.delay(str(cid))
        dispatched += 1
    if dispatched:
        logger.info("dispatch_due_campaigns queued %d campaign(s)", dispatched)
    return dispatched


@shared_task(bind=True, max_retries=3, queue='campaigns')
def dispatch_single_message(self, log_id):
    """Retry a single failed CommunicationLog by creating a new one."""
    try:
        old = CommunicationLog.objects.select_related('campaign').get(id=log_id)
    except CommunicationLog.DoesNotExist:
        return None
    # Don't resurrect sends for a campaign that is no longer actively running.
    if old.campaign.status not in ('running', 'scheduled'):
        logger.info(
            "Skipping retry for log %s; campaign %s status=%s.",
            log_id, old.campaign_id, old.campaign.status,
        )
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

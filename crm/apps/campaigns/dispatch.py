import logging
import random
import httpx
from django.conf import settings
from django.utils import timezone
from .models import Campaign, CommunicationLog
from .personaliser import render
from apps.segments.evaluator import SegmentEvaluator

logger = logging.getLogger(__name__)


class CampaignDispatcher:
    """Build CommunicationLog rows and POST to channel_stub."""

    def __init__(self, campaign: Campaign):
        self.campaign = campaign

    def audience(self):
        return SegmentEvaluator().evaluate(self.campaign.segment.filter_tree)

    def _pick_variant(self):
        if not self.campaign.is_ab_test or not self.campaign.ab_variants:
            return None, self.campaign.message_template
        weights = [v.get('weight_pct', 100 / len(self.campaign.ab_variants)) for v in self.campaign.ab_variants]
        v = random.choices(self.campaign.ab_variants, weights=weights, k=1)[0]
        return v.get('label', ''), v.get('message_template', self.campaign.message_template)

    def _resolve_channel(self, customer) -> str:
        if self.campaign.channel == 'auto':
            return customer.channel_preference if customer.channel_preference != 'auto' else 'whatsapp'
        return self.campaign.channel

    def dispatch(self):
        customers = list(self.audience())
        self.campaign.status = 'running'
        self.campaign.launched_at = timezone.now()
        self.campaign.stat_total = len(customers)
        self.campaign.save(update_fields=['status', 'launched_at', 'stat_total'])

        sent = 0
        for customer in customers:
            label, template = self._pick_variant()
            channel = self._resolve_channel(customer)
            body = render(template, customer)
            log = CommunicationLog.objects.create(
                campaign=self.campaign,
                customer=customer,
                channel=channel,
                message_body=body,
                variant_label=label or '',
                status='queued',
            )
            if self._send_to_stub(log, customer):
                sent += 1
        return sent

    def _send_to_stub(self, log, customer) -> bool:
        recipient = customer.email if log.channel == 'email' else customer.phone
        if not recipient:
            log.status = 'failed'
            log.failure_reason = 'no_contact'
            log.save(update_fields=['status', 'failure_reason'])
            return False
        callback_url = f"{settings.SITE_URL.rstrip('/')}/api/v1/webhooks/channel-event/"
        try:
            with httpx.Client(timeout=10.0) as client:
                resp = client.post(
                    f"{settings.CHANNEL_STUB_URL}/send",
                    json={
                        'message_id': str(log.id),
                        'recipient': recipient,
                        'channel': log.channel,
                        'message_body': log.message_body,
                        'callback_url': callback_url,
                        'batch_size': self.campaign.stat_total,
                    },
                )
                resp.raise_for_status()
                data = resp.json()
                log.stub_message_id = data.get('stub_message_id', '')
                log.save(update_fields=['stub_message_id'])
                return True
        except httpx.HTTPError as e:
            logger.exception("Stub send failed for log %s", log.id)
            log.status = 'failed'
            log.failure_reason = 'stub_error'
            log.save(update_fields=['status', 'failure_reason'])
            return False

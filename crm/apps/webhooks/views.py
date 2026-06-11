import json
import logging
from django.core.cache import cache
from django.db import transaction, IntegrityError
from django.db.models import F
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from apps.core.utils import hmac_verify
from apps.campaigns.models import CommunicationLog, CommunicationEvent, Campaign
from .state_machine import CommunicationStateMachine

logger = logging.getLogger(__name__)


_STAT_FIELD = {
    'sent': 'stat_sent',
    'delivered': 'stat_delivered',
    'failed': 'stat_failed',
    'opened': 'stat_opened',
    'read': 'stat_read',
    'clicked': 'stat_clicked',
}


def _broadcast_event(log, event_type):
    layer = get_channel_layer()
    if layer is None:
        return
    payload = {
        'type': 'channel_event',
        'data': {
            'log_id': str(log.id),
            'campaign_id': str(log.campaign_id),
            'customer_id': str(log.customer_id),
            'event_type': event_type,
            'channel': log.channel,
            'timestamp': timezone.now().isoformat(),
        },
    }
    async_to_sync(layer.group_send)('events', payload)


def _maybe_smart_retry(log):
    from apps.campaigns.tasks import dispatch_single_message
    if log.status != 'failed':
        return
    reason = log.failure_reason
    if reason in ('network_timeout', 'inbox_full') and log.retry_count < 2:
        dispatch_single_message.apply_async(args=[str(log.id)], countdown=1800)
    elif reason == 'rate_limited' and log.retry_count < 2:
        dispatch_single_message.apply_async(args=[str(log.id)], countdown=3600)


class ChannelEventWebhookView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        body = request.body
        sig = request.headers.get('X-Xeno-Signature', '')
        if not hmac_verify(body, sig):
            return Response({'error': 'invalid signature'}, status=401)

        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            return Response({'error': 'invalid json'}, status=400)

        message_id = payload.get('message_id')
        event_type = payload.get('event_type')
        if not message_id or not event_type:
            return Response({'error': 'missing fields'}, status=400)

        # Dedup: drop duplicate events at the edge.
        dedup_key = f"webhook:{message_id}:{event_type}"
        if cache.get(dedup_key):
            return Response({'status': 'duplicate'}, status=200)
        cache.set(dedup_key, 1, timeout=86400)

        occurred_at = parse_datetime(payload.get('occurred_at') or '') or timezone.now()
        metadata = payload.get('metadata') or {}

        broadcast_event_type = None
        with transaction.atomic():
            try:
                log = CommunicationLog.objects.select_for_update().get(id=message_id)
            except CommunicationLog.DoesNotExist:
                return Response({'error': 'log not found'}, status=404)

            applied = CommunicationStateMachine.apply(log, event_type, occurred_at, metadata)
            if not applied:
                return Response({'status': 'ignored'}, status=200)

            log.save()

            try:
                CommunicationEvent.objects.create(
                    log=log, event_type=event_type, occurred_at=occurred_at, metadata=metadata,
                )
            except IntegrityError:
                # Duplicate — already counted.
                pass
            else:
                stat_field = _STAT_FIELD.get(event_type)
                if stat_field:
                    Campaign.objects.filter(id=log.campaign_id).update(
                        **{stat_field: F(stat_field) + 1}
                    )
            broadcast_event_type = event_type

        # Outside transaction
        log.refresh_from_db()
        _broadcast_event(log, broadcast_event_type)
        _maybe_smart_retry(log)

        return Response({'status': 'ok'})

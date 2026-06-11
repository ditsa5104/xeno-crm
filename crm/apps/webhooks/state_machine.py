import logging
from django.utils import timezone
from apps.campaigns.models import CommunicationLog

logger = logging.getLogger(__name__)


VALID_TRANSITIONS = {
    'queued':    ['sent', 'failed'],
    'sent':      ['delivered', 'failed'],
    'delivered': ['opened', 'clicked', 'failed'],
    'opened':    ['read', 'clicked'],
    'read':      ['clicked'],
    'clicked':   [],
    'failed':    [],
}


_TIMESTAMP_FIELD = {
    'sent': 'sent_at',
    'delivered': 'delivered_at',
    'opened': 'opened_at',
    'read': 'read_at',
    'clicked': 'clicked_at',
}


class CommunicationStateMachine:
    @staticmethod
    def can_transition(current: str, target: str) -> bool:
        return target in VALID_TRANSITIONS.get(current, [])

    @staticmethod
    def apply(log: CommunicationLog, event_type: str, occurred_at, metadata: dict) -> bool:
        # Allow advancing to any state we haven't yet reached
        if not CommunicationStateMachine.can_transition(log.status, event_type):
            # Ignore but don't error: out-of-order or duplicate
            logger.info("Ignoring transition %s -> %s on log %s", log.status, event_type, log.id)
            return False
        log.status = event_type
        ts_field = _TIMESTAMP_FIELD.get(event_type)
        if ts_field and not getattr(log, ts_field):
            setattr(log, ts_field, occurred_at or timezone.now())
        if event_type == 'failed':
            log.failure_reason = (metadata or {}).get('reason', '')
        return True

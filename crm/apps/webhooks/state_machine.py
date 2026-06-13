import logging
from django.utils import timezone
from apps.campaigns.models import CommunicationLog

logger = logging.getLogger(__name__)


# Engagement is a monotonic funnel. Each event carries a rank; a customer who
# clicked necessarily also opened and received the message, even if those
# callbacks arrive later or out of order. We therefore do NOT gate on a strict
# linear transition table (which silently dropped reordered events). Instead we
# record every event's timestamp and derive status as the furthest stage reached.
EVENT_RANK = {
    'sent': 1,
    'delivered': 2,
    'opened': 3,
    'read': 4,
    'clicked': 5,
}

# Order matters: furthest (highest-rank) recorded timestamp wins for status.
_STATUS_BY_FIELD = [
    ('clicked', 'clicked_at'),
    ('read', 'read_at'),
    ('opened', 'opened_at'),
    ('delivered', 'delivered_at'),
    ('sent', 'sent_at'),
]

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
        """Legacy linear check, retained for callers/tests that reason about the
        forward funnel order. Not used to gate ingestion anymore."""
        order = ['queued', 'sent', 'delivered', 'opened', 'read', 'clicked']
        try:
            return order.index(target) > order.index(current)
        except ValueError:
            return False

    @staticmethod
    def _derive_status(log: CommunicationLog) -> str:
        for status, field in _STATUS_BY_FIELD:
            if getattr(log, field):
                return status
        return log.status or 'queued'

    @staticmethod
    def apply(log: CommunicationLog, event_type: str, occurred_at, metadata: dict) -> bool:
        """Apply one channel callback, tolerant of out-of-order delivery.

        Returns True if this event was newly recorded (so the caller should log a
        CommunicationEvent and bump the stat), False if it was a duplicate or an
        invalid event that should be ignored.
        """
        ts = occurred_at or timezone.now()

        if event_type == 'failed':
            # A message that was actually delivered/engaged cannot also be a
            # failure — success wins over a (possibly stale, reordered) failure.
            if log.delivered_at or log.opened_at or log.read_at or log.clicked_at:
                logger.info("Ignoring 'failed' after success on log %s", log.id)
                return False
            if log.status == 'failed':
                return False  # duplicate failure
            log.status = 'failed'
            log.failure_reason = (metadata or {}).get('reason', '')
            return True

        if event_type not in EVENT_RANK:
            logger.info("Ignoring unknown event %s on log %s", event_type, log.id)
            return False

        ts_field = _TIMESTAMP_FIELD[event_type]
        if getattr(log, ts_field):
            # Already recorded this stage — duplicate, ignore (don't double-count).
            return False

        setattr(log, ts_field, ts)
        # A real engagement event proves the message was not a failure.
        if log.status == 'failed':
            log.failure_reason = ''
        # Status = furthest stage reached, regardless of arrival order.
        log.status = CommunicationStateMachine._derive_status(log)
        return True

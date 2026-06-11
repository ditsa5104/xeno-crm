import logging
from django.utils import timezone
from celery import shared_task
from .models import Segment, SegmentSnapshot
from .evaluator import SegmentEvaluator

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def recompute_segment_memberships(self):
    logger.info("Recomputing segment memberships")
    n = 0
    for seg in Segment.objects.filter(segment_type='dynamic'):
        try:
            qs = SegmentEvaluator().evaluate(seg.filter_tree)
            count = qs.count()
            SegmentSnapshot.objects.create(segment=seg, customer_count=count)
            seg.customer_count = count
            seg.last_computed = timezone.now()
            seg.save(update_fields=['customer_count', 'last_computed'])
            n += 1
        except Exception:
            logger.exception("Segment %s recompute failed", seg.id)
    return n

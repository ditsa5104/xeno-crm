import logging
from celery import shared_task
from .scoring import RFMScorer

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, queue='scoring')
def recompute_rfm_scores(self):
    logger.info("RFM recompute starting")
    try:
        n = RFMScorer().compute_all()
        logger.info("RFM recompute done: %d customers", n)
        return n
    except Exception as exc:
        logger.exception("RFM recompute failed")
        raise self.retry(exc=exc, countdown=60)

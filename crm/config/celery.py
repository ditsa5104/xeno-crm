import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')

app = Celery('xeno')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Free-tier memory guards (512MB dyno shared with daphne + beat):
# - prefetch 1 task at a time so a single worker doesn't hold many in memory
# - restart the child if it exceeds ~200MB RSS to reclaim leaked memory
app.conf.worker_prefetch_multiplier = 1
app.conf.worker_max_tasks_per_child = 100
app.conf.worker_max_memory_per_child = 200_000  # KB (~200MB)

app.conf.beat_schedule = {
    'recompute-rfm-scores': {
        'task': 'apps.customers.tasks.recompute_rfm_scores',
        'schedule': crontab(hour=0, minute=0),
    },
    'recompute-segment-memberships': {
        'task': 'apps.segments.tasks.recompute_segment_memberships',
        'schedule': crontab(hour=1, minute=0),
    },
    'run-revenue-attribution': {
        'task': 'apps.analytics.tasks.run_revenue_attribution',
        'schedule': crontab(hour=2, minute=0),
    },
    'select-ab-winners': {
        'task': 'apps.campaigns.tasks.select_ab_winners',
        'schedule': crontab(minute='*/30'),
    },
}

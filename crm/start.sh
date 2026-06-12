#!/usr/bin/env bash
# Free-tier startup: migrate, then run a single Celery worker (with embedded
# beat) as a background process, then start daphne in the foreground.
set -e

echo "Running migrations..."
python manage.py migrate --noinput

echo "Starting Celery worker (with embedded beat)..."
# Free-tier memory guard. The whole stack shares one 512MB dyno, so keep the
# process count and per-process memory low:
#  - default prefork pool forks one child per CPU core (8+ on Render shared
#    hosts), so pin --concurrency=1 to fork exactly one child.
#  - -B embeds beat in the worker instead of a separate process (~120MB saved).
#  - recycle the child after 100 tasks to bound memory growth.
celery -A config worker \
  -l warning \
  -Q default,campaigns,scoring \
  --concurrency=1 \
  --max-tasks-per-child=100 \
  --beat --scheduler django_celery_beat.schedulers:DatabaseScheduler \
  --without-gossip --without-mingle --without-heartbeat &

echo "Starting daphne..."
exec daphne -b 0.0.0.0 -p "$PORT" config.asgi:application

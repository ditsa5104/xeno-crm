#!/usr/bin/env bash
# Free-tier startup: migrate, then run Celery worker + beat as background
# processes, then start daphne in the foreground.
set -e

echo "Running migrations..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

echo "Starting Celery worker..."
celery -A config worker -l info -Q default,campaigns,scoring &

echo "Starting Celery beat..."
celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler &

echo "Starting daphne..."
exec daphne -b 0.0.0.0 -p "$PORT" config.asgi:application

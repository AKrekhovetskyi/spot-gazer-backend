#!/bin/sh

set -e  # Exit on error

echo "Applying database migrations..."
poetry run python manage.py migrate

echo "Collecting static files..."
poetry run python manage.py collectstatic --noinput

echo "Starting Celery..."
celery -A django_core worker -B --loglevel=info --logfile="$(pwd)/celery.log" --detach

echo "Starting Django server..."
poetry run python manage.py runserver 0.0.0.0:8000

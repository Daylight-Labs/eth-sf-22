#!/usr/bin/env bash
set -eou pipefail

if [ "$ENVIRONMENT" == "dev" ] ; then
    python manage.py collectstatic --no-input
    python manage.py migrate
else
    echo "running migrations"
    python manage.py migrate
fi

# start background tasks
gunicorn api.wsgi:application --bind :8000
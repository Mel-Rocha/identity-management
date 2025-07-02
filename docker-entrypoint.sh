#!/bin/bash

echo "Apply database migrations"
python3 manage.py migrate

echo "Collect static files"
python3 manage.py collectstatic --noinput

# Start application
echo "Start application"
exec gunicorn config.wsgi:application -c gunicorn_config.py
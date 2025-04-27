#!/bin/bash

# Wait for database to be ready (uncomment if needed)
# sleep 5

# Apply database migrations
cd /app/huawei_prototype
python manage.py migrate --noinput

# Collect static files
python manage.py collectstatic --noinput

# Start Gunicorn
exec gunicorn --bind 0.0.0.0:8000 huawei_prototype.wsgi:application
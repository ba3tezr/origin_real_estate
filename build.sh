#!/bin/bash
set -e

echo "Activating virtual environment..."
source /opt/venv/bin/activate

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Build completed successfully!"


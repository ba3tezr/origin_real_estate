#!/bin/bash
set -e

echo "Creating virtual environment..."
python3 -m venv /opt/venv

echo "Activating virtual environment..."
source /opt/venv/bin/activate

echo "Upgrading pip..."
pip install --upgrade pip

echo "Installing requirements..."
pip install -r requirements.txt

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Build completed successfully!"


#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Apply migrations
python ReportingBackend/manage.py migrate

# Create superuser if environment variable is set
#if [[ $CREATE_SUPERUSER ]]; then
  #python ReportingBackend/manage.py createsuperuser --no-input
#fi

# Collect static files (uncomment if you need this)
# python ReportingBackend/manage.py collectstatic --no-input
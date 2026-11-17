#!/usr/bin/env bash
set -o errexit

python -m pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate --no-input

# Load seed data (students, instructors, courses, enrollments, etc.)
# This includes the admin superuser and all LMS data.
python manage.py loaddata deploy-data.json

# Ensure the admin superuser exists even if the fixture was skipped/modified.
python manage.py create_superusers

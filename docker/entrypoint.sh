#!/bin/sh

# Stop on errors
set -e

python manage.py migrate
python manage.py collectstatic --noinput

# This executes the CMD provided in the Dockerfile
exec "$@"
#!/usr/bin/env bash
set -euo pipefail

# Navigate to project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${SCRIPT_DIR}/.."
cd "${PROJECT_ROOT}"

export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-config.settings}"
export DEBUG="${DEBUG:-False}"
export ALLOWED_HOSTS="${ALLOWED_HOSTS:-178.218.200.120,localhost,127.0.0.1}"
export CORS_ALLOWED_ORIGINS="${CORS_ALLOWED_ORIGINS:-http://178.218.200.120:1596,http://localhost:3000}"
export CSRF_TRUSTED_ORIGINS="${CSRF_TRUSTED_ORIGINS:-http://178.218.200.120:1596,http://localhost:3000}"
export PORT="${PORT:-1596}"

python manage.py migrate --noinput
python manage.py collectstatic --noinput

echo "Starting Gunicorn on port ${PORT}"
exec gunicorn config.wsgi:application --bind "0.0.0.0:${PORT}" --workers "${GUNICORN_WORKERS:-3}"

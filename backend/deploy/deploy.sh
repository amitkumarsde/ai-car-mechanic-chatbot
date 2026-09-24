#!/usr/bin/env bash
# Pull new code and restart the API. Run on the server: bash ~/app/backend/deploy/deploy.sh
set -euo pipefail

cd /home/ubuntu/app
git pull --ff-only

cd backend
bash deploy/backup_db.sh
venv/bin/pip install -r requirements.txt
venv/bin/python manage.py migrate --noinput
venv/bin/python manage.py collectstatic --noinput
sudo systemctl restart gunicorn

sleep 2
sudo systemctl is-active --quiet gunicorn && echo "API is running"

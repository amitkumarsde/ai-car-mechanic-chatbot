#!/usr/bin/env bash
# One-time setup on a fresh Ubuntu EC2 server. Run: bash setup_server.sh YOUR_DOMAIN
set -euo pipefail

DOMAIN="${1:?Usage: bash setup_server.sh YOUR_DOMAIN}"
APP_DIR=/home/ubuntu/app
DATA_DIR=/var/lib/carbot

sudo apt update
sudo apt install -y python3-venv python3-pip nginx sqlite3 certbot python3-certbot-nginx

# 1 GB swap so the small free tier server does not run out of memory
if [ ! -f /swapfile ]; then
  sudo fallocate -l 1G /swapfile
  sudo chmod 600 /swapfile
  sudo mkswap /swapfile
  sudo swapon /swapfile
  echo "/swapfile none swap sw 0 0" | sudo tee -a /etc/fstab
fi

sudo mkdir -p "$DATA_DIR/media" "$DATA_DIR/static" "$DATA_DIR/backups"
sudo chown -R ubuntu:www-data "$DATA_DIR"
sudo chmod 750 "$DATA_DIR"

cd "$APP_DIR/backend"
python3 -m venv venv
venv/bin/pip install --upgrade pip
venv/bin/pip install -r requirements.txt

if [ ! -f .env ]; then
  echo "Create $APP_DIR/backend/.env first (see .env.example), then run this script again."
  exit 1
fi
chmod 600 .env

venv/bin/python manage.py migrate --noinput
venv/bin/python manage.py collectstatic --noinput
venv/bin/python manage.py check --deploy

sudo cp deploy/gunicorn.service /etc/systemd/system/gunicorn.service
sudo systemctl daemon-reload
sudo systemctl enable --now gunicorn

sed "s/YOUR_DOMAIN/$DOMAIN/" deploy/nginx.conf | sudo tee /etc/nginx/sites-available/carbot > /dev/null
sudo ln -sf /etc/nginx/sites-available/carbot /etc/nginx/sites-enabled/carbot
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx

(crontab -l 2>/dev/null | grep -v backup_db.sh; echo "0 2 * * * $APP_DIR/backend/deploy/backup_db.sh >> $DATA_DIR/backups/backup.log 2>&1") | crontab -

echo "Done. Now run: sudo certbot --nginx -d $DOMAIN"

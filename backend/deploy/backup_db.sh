#!/usr/bin/env bash
# Safe copy of the SQLite database while the app is running; keeps the last 7 days
set -euo pipefail

DB=/var/lib/carbot/db.sqlite3
BACKUP_DIR=/var/lib/carbot/backups
FILE="$BACKUP_DIR/db-$(date +%F-%H%M).sqlite3"

[ -f "$DB" ] || { echo "No database yet at $DB"; exit 0; }

sqlite3 "$DB" ".backup '$FILE'"
gzip "$FILE"
find "$BACKUP_DIR" -name "db-*.sqlite3.gz" -mtime +7 -delete

echo "Backup saved: $FILE.gz"

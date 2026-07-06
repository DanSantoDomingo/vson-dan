#!/usr/bin/env bash
# Dump the Postgres container's database to a gzipped file and prune old ones.
# Runs daily from cron on the droplet.
set -euo pipefail

BACKUP_DIR="/opt/vson/backups"
DB="vision_template"
KEEP_DAYS=14

mkdir -p "$BACKUP_DIR"
stamp="$(date +%Y%m%d-%H%M%S)"
file="$BACKUP_DIR/${DB}-${stamp}.sql.gz"

docker exec vson-db pg_dump -U postgres "$DB" | gzip > "$file"
echo "backup written: $file"

find "$BACKUP_DIR" -name "${DB}-*.sql.gz" -mtime +"$KEEP_DAYS" -delete
echo "pruned backups older than ${KEEP_DAYS} days"

#!/bin/bash
# Бэкап базы данных

BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/dating_$TIMESTAMP.sql"

mkdir -p $BACKUP_DIR

echo "Creating backup: $BACKUP_FILE"
docker exec dating-postgres pg_dump -U postgres Dating_site > $BACKUP_FILE
echo "Backup created: $BACKUP_FILE"
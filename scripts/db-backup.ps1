$BACKUP_DIR = ".\backups"
$TIMESTAMP = Get-Date -Format "yyyyMMdd_HHmmss"
$BACKUP_FILE = "$BACKUP_DIR\dating_$TIMESTAMP.sql"

New-Item -ItemType Directory -Force -Path $BACKUP_DIR | Out-Null

Write-Host "Creating backup: $BACKUP_FILE"
docker exec dating-postgres pg_dump -U postgres Dating_site > $BACKUP_FILE
Write-Host "Backup created: $BACKUP_FILE"
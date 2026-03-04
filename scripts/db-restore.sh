if [ -z "$1" ]; then
    echo "❌ Usage: ./scripts/db-restore.sh <backup-file>"
    exit 1
fi

echo "This will overwrite the current database!"
read -p "Are you sure? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

echo "Restoring from $1"
cat "$1" | docker exec -i dating-postgres psql -U postgres Dating_site
echo "Restore complete"
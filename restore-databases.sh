#!/bin/bash

# Restore Databases Script
# This restores PostgreSQL and MongoDB databases from backups
# Run this after starting containers to restore your data

BACKUP_DIR="./database-backups"

echo "🔄 Restoring databases from backups..."

# Check if backup directory exists
if [ ! -d "$BACKUP_DIR" ]; then
    echo "❌ Backup directory not found: $BACKUP_DIR"
    echo "   Please run ./backup-databases.sh first to create backups."
    exit 1
fi

# Check if containers are running
if ! docker ps | grep -q p2p-postgres; then
    echo "❌ PostgreSQL container is not running. Please start containers first."
    exit 1
fi

if ! docker ps | grep -q p2p-mongodb; then
    echo "❌ MongoDB container is not running. Please start containers first."
    exit 1
fi

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
until docker exec p2p-postgres pg_isready -U postgres > /dev/null 2>&1; do
    sleep 2
done

# Find latest PostgreSQL backup
LATEST_PG_BACKUP=$(ls -t $BACKUP_DIR/postgres_backup_*.sql 2>/dev/null | head -n1)
if [ -z "$LATEST_PG_BACKUP" ]; then
    echo "⚠️  No PostgreSQL backup found. Skipping PostgreSQL restore."
else
    echo "📦 Restoring PostgreSQL from: $(basename $LATEST_PG_BACKUP)"
    cat "$LATEST_PG_BACKUP" | docker exec -i p2p-postgres psql -U postgres
    echo "  ✅ PostgreSQL restored successfully"
fi

# Wait for MongoDB to be ready
echo "⏳ Waiting for MongoDB to be ready..."
until docker exec p2p-mongodb mongosh --eval "db.adminCommand('ping')" > /dev/null 2>&1; do
    sleep 2
done

# Find latest MongoDB backup
LATEST_MONGO_BACKUP=$(ls -t $BACKUP_DIR/mongo_backup_*.archive 2>/dev/null | head -n1)
if [ -z "$LATEST_MONGO_BACKUP" ]; then
    echo "⚠️  No MongoDB backup found. Skipping MongoDB restore."
else
    echo "📦 Restoring MongoDB from: $(basename $LATEST_MONGO_BACKUP)"
    docker cp "$LATEST_MONGO_BACKUP" p2p-mongodb:/tmp/mongo_restore.archive
    docker exec p2p-mongodb mongorestore --archive=/tmp/mongo_restore.archive
    echo "  ✅ MongoDB restored successfully"
fi

echo ""
echo "✅ Restore complete!"
echo ""
echo "📊 Database Status:"
docker exec p2p-postgres psql -U postgres -c "\l" | grep -E "p2p_sandbox|supertokens"
echo ""
echo "To verify data:"
echo "  PostgreSQL: docker exec -it p2p-postgres psql -U postgres -d p2p_sandbox"
echo "  MongoDB: docker exec -it p2p-mongodb mongosh p2p_sandbox"
#!/bin/bash

# Backup Databases Script
# This creates backups of PostgreSQL and MongoDB databases
# Run this before stopping Docker Desktop to preserve your data

BACKUP_DIR="./database-backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "🔒 Creating database backups..."

# Create backup directory
mkdir -p $BACKUP_DIR

# Check if containers are running
if ! docker ps | grep -q p2p-postgres; then
    echo "❌ PostgreSQL container is not running. Please start containers first."
    exit 1
fi

if ! docker ps | grep -q p2p-mongodb; then
    echo "❌ MongoDB container is not running. Please start containers first."
    exit 1
fi

# Backup PostgreSQL databases
echo "📦 Backing up PostgreSQL databases..."
docker exec p2p-postgres pg_dumpall -U postgres > "$BACKUP_DIR/postgres_backup_$TIMESTAMP.sql"
echo "  ✅ PostgreSQL backup created: postgres_backup_$TIMESTAMP.sql"

# Backup MongoDB database
echo "📦 Backing up MongoDB database..."
docker exec p2p-mongodb mongodump --archive=/tmp/mongo_backup.archive --db=p2p_sandbox
docker cp p2p-mongodb:/tmp/mongo_backup.archive "$BACKUP_DIR/mongo_backup_$TIMESTAMP.archive"
echo "  ✅ MongoDB backup created: mongo_backup_$TIMESTAMP.archive"

# Keep only last 5 backups to save space
echo "🧹 Cleaning old backups (keeping last 5)..."
ls -t $BACKUP_DIR/postgres_backup_*.sql | tail -n +6 | xargs -r rm
ls -t $BACKUP_DIR/mongo_backup_*.archive | tail -n +6 | xargs -r rm

echo ""
echo "✅ Backup complete!"
echo "📁 Backups stored in: $BACKUP_DIR"
echo ""
echo "To restore from these backups, run: ./restore-databases.sh"
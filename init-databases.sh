#!/bin/bash

# Database Initialization Script
# This script creates the SuperTokens database and seeds test data
# Run this after starting containers for the first time

echo "🚀 Initializing P2P Sandbox Databases..."

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
until docker exec p2p-postgres pg_isready -U postgres > /dev/null 2>&1; do
    sleep 2
done
echo "✅ PostgreSQL is ready!"

# Create SuperTokens database
echo "📦 Creating SuperTokens database..."
docker exec p2p-postgres psql -U postgres -c "CREATE DATABASE supertokens;" 2>/dev/null || echo "  Database already exists"

# Create main application database (if needed)
echo "📦 Ensuring main database exists..."
docker exec p2p-postgres psql -U postgres -c "CREATE DATABASE p2p_sandbox;" 2>/dev/null || echo "  Database already exists"

# Wait for MongoDB to be ready
echo "⏳ Waiting for MongoDB to be ready..."
until docker exec p2p-mongodb mongosh --eval "db.adminCommand('ping')" > /dev/null 2>&1; do
    sleep 2
done
echo "✅ MongoDB is ready!"

# Run database migrations
echo "🔄 Running database migrations..."
docker exec p2p-backend alembic upgrade head 2>/dev/null || echo "  Migrations may have already been applied"

# Seed the databases
echo "🌱 Seeding databases with test data..."
docker exec p2p-backend python scripts/seed_all.py seed 2>/dev/null || {
    echo "  Seeding might have failed or data already exists"
    echo "  You can manually run: docker exec p2p-backend python scripts/seed_all.py reset"
}

echo ""
echo "✅ Database initialization complete!"
echo ""
echo "📊 Database Status:"
echo "  - PostgreSQL: Running on port 5432"
echo "  - MongoDB: Running on port 27017"
echo "  - SuperTokens database: Created"
echo "  - Test data: Seeded (if successful)"
echo ""
echo "🔗 Access Points:"
echo "  - Frontend: http://localhost:5173"
echo "  - Backend API: http://localhost:8000/docs"
echo "  - SuperTokens: http://localhost:3567"
echo ""
echo "💾 Data is persisted in ./docker-volumes/ directory"
echo "   This data will survive Docker Desktop restarts!"
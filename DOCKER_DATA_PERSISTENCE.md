# Docker Data Persistence Solution

## The Problem
When Docker Desktop restarts (especially on Windows with WSL), Docker volumes can be lost, causing:
- Loss of all database data
- Missing SuperTokens database
- Need to re-seed data every time
- Frustration and lost development time

## The Solution

### 1. Backup and Restore Strategy
We've implemented a backup/restore system that saves your data to local files that persist outside of Docker.

### 2. Scripts Created

#### `backup-databases.sh`
- Creates timestamped backups of PostgreSQL and MongoDB
- Stores backups in `./database-backups/` directory
- Keeps only the last 5 backups to save space
- Run this BEFORE stopping Docker Desktop

#### `restore-databases.sh`
- Restores databases from the latest backup
- Automatically finds and restores most recent backup files
- Run this AFTER starting Docker containers

#### `init-databases.sh`
- Creates SuperTokens database (always needed on fresh start)
- Runs database migrations
- Seeds initial test data
- Run this for first-time setup

## Recommended Workflow

### Before Stopping Work
```bash
# Create backup of your current data
./backup-databases.sh

# Then you can safely stop containers
docker-compose down
```

### When Starting Work
```bash
# Start containers
docker-compose up -d

# If SuperTokens fails, create its database
docker exec p2p-postgres psql -U postgres -c "CREATE DATABASE supertokens;"
docker start p2p-supertokens

# Restore your data from backup
./restore-databases.sh
```

### First Time Setup
```bash
# Start containers
docker-compose up -d

# Initialize databases and seed data
./init-databases.sh

# Create initial backup
./backup-databases.sh
```

## Alternative Solution (Not Recommended for WSL)
We initially tried using bind mounts (`./docker-volumes/`) but this has permission issues on WSL. The backup/restore approach is more reliable.

## Important Files
- `./database-backups/` - Contains your database backups (git-ignored)
- `./docker-volumes/` - Can be deleted (not used anymore)
- `.gitignore` - Updated to ignore backup directories

## Troubleshooting

### SuperTokens Won't Start
```bash
# SuperTokens always needs its database created
docker exec p2p-postgres psql -U postgres -c "CREATE DATABASE supertokens;"
docker start p2p-supertokens
```

### Tables Don't Exist
```bash
# Create tables directly
docker exec p2p-backend python -c "
from app.db.session import engine
from app.models import *
import asyncio
asyncio.run(engine.begin().run_sync(BaseModel.metadata.create_all))
"
```

### Want Fresh Data
```bash
# Reset and seed everything
docker exec p2p-backend python scripts/seed_all.py reset
```

## Why This Happens
Docker Desktop on Windows/WSL has known issues with volume persistence. Named volumes are managed by Docker and can be lost when:
- Docker Desktop updates
- Windows restarts
- WSL2 backend restarts
- Docker Desktop resets

Our backup solution works around this by storing data in regular files that persist outside Docker's control.

## Future Improvements
Consider using:
- External PostgreSQL/MongoDB instances
- Cloud databases for development
- Docker volumes stored on Windows filesystem (not WSL)
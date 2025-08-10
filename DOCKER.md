# Docker Setup for P2P Sandbox

## Docker Files Reference

### 📁 Configuration Files
| File | Purpose | Location |
|------|---------|----------|
| **docker-compose.yml** | Main orchestration file | `/docker-compose.yml` |
| **docker-compose.prod.yml** | Production overrides | `/docker-compose.prod.yml` |
| **docker-control.sh** | Management script with all commands | `/docker-control.sh` |
| **.env.docker** | Docker environment variables | `/.env.docker` |
| **.env.example** | Environment template for developers | `/.env.example` |

### 🐳 Container Definitions
| Service | Development | Production | Purpose |
|---------|-------------|------------|---------|
| **Backend** | `p2p-backend-app/Dockerfile.dev` | `p2p-backend-app/Dockerfile` | FastAPI server |
| **Frontend** | `p2p-frontend-app/Dockerfile.dev` | `p2p-frontend-app/Dockerfile` | React app + Nginx |

### ⚙️ Configuration & Support Files
| File | Purpose | Location |
|------|---------|----------|
| **nginx.conf** | Production frontend web server config | `p2p-frontend-app/nginx.conf` |
| **.dockerignore** | Frontend Docker ignore rules | `p2p-frontend-app/.dockerignore` |
| **init-postgres.sql** | PostgreSQL database initialization | `docker/scripts/init-postgres.sql` |
| **init-mongo.js** | MongoDB database initialization | `docker/scripts/init-mongo.js` |
| **vite.config.ts** | Frontend dev server (Docker-compatible) | `p2p-frontend-app/vite.config.ts` |

### 📚 Documentation Files
| File | Purpose | Location |
|------|---------|----------|
| **DOCKER.md** | This file - comprehensive Docker guide | `/DOCKER.md` |
| **README.md** | Main developer guide (includes Docker quick start) | `/README.md` |
| **CONTRIBUTING.md** | Development workflow (includes Docker workflow) | `/CONTRIBUTING.md` |
| **application-startup-guide.md** | Updated startup guide with Docker-first approach | `docs/aadil_docs/application-startup-guide.md` |

### 🗄️ Legacy Files (Reference Only)
| File | Status | Purpose |
|------|--------|---------|
| `p2p-backend-app/start-docker-with-claude.sh` | 🔴 Legacy | Old startup script |
| `p2p-frontend-app/frontend-control.sh` | 🔴 Legacy | Old frontend control script |
| `docs/stories/epic-01/story-06-docker-containerization.md` | 📚 Archive | Original Docker epic story |

## Quick Start

### First Time Setup
```bash
# Start all containers
./docker-control.sh start

# Initialize databases and seed test data
./init-databases.sh

# Create initial backup
./backup-databases.sh
```

### Daily Development Workflow

**Starting Work:**
```bash
# Start containers
./docker-control.sh start

# Restore your data (if needed)
./restore-databases.sh
```

**Stopping Work:**
```bash
# Backup your data before stopping
./backup-databases.sh

# Stop containers
./docker-control.sh stop
```

## Services

The following services run in Docker containers:

| Service | Container | Ports | Purpose |
|---------|-----------|-------|---------|
| Frontend | `p2p-frontend` | 5173 | React app with hot reload |
| Backend | `p2p-backend` | 8000, 5678 | FastAPI server + debug port |
| PostgreSQL | `p2p-postgres` | 5432 | Main database |
| MongoDB | `p2p-mongodb` | 27017 | Document storage |
| SuperTokens | `p2p-supertokens` | 3567 | Authentication service |

## Access Points

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000  
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Commands

Use the `docker-control.sh` script for easy management:

```bash
# Start all services
./docker-control.sh start

# Stop all services  
./docker-control.sh stop

# Restart all services
./docker-control.sh restart

# Show status
./docker-control.sh status

# View logs (all services)
./docker-control.sh logs

# View logs (specific service)
./docker-control.sh logs backend

# Execute command in container
./docker-control.sh exec backend python -m pytest

# Rebuild services
./docker-control.sh rebuild

# Clean up everything
./docker-control.sh clean
```

## Development Workflow

1. **Start Development Environment:**
   ```bash
   ./docker-control.sh start
   ```

2. **Make Code Changes:**
   - Frontend: Changes in `p2p-frontend-app/` auto-reload
   - Backend: Changes in `p2p-backend-app/` auto-reload

3. **View Logs:**
   ```bash
   ./docker-control.sh logs frontend
   ./docker-control.sh logs backend
   ```

4. **Run Tests:**
   ```bash
   ./docker-control.sh exec backend python -m pytest
   ```

## File Structure

```
P2P-V2/
├── docker-compose.yml          # Main orchestration file
├── .env.docker                 # Docker environment variables
├── docker-control.sh           # Management script
├── docker/                     # Docker support files
│   └── scripts/               # Database init scripts
├── p2p-frontend-app/
│   ├── Dockerfile.dev         # Development image
│   ├── Dockerfile             # Production image
│   ├── nginx.conf             # Production nginx config
│   └── .dockerignore
└── p2p-backend-app/
    ├── Dockerfile.dev         # Development image
    └── Dockerfile             # Production image
```

## Environment Variables

Docker-specific environment variables are in `.env.docker`:

- Database connections use container service names
- Frontend uses localhost URLs (browser access)
- Hot reload enabled for development

## Troubleshooting

### Services Not Starting
```bash
# Check status
./docker-control.sh status

# View logs
./docker-control.sh logs

# Restart specific service
docker-compose restart backend
```

### Port Conflicts
```bash
# Kill processes on conflicting ports
sudo lsof -ti :5173 | xargs kill
sudo lsof -ti :8000 | xargs kill
```

### Database Issues
```bash
# Access PostgreSQL
docker exec p2p-postgres psql -U postgres -d p2p_sandbox

# Access MongoDB
docker exec p2p-mongodb mongosh p2p_sandbox
```

### Hot Reload Not Working
- Ensure `CHOKIDAR_USEPOLLING=true` in environment
- Verify file permissions in container
- Check vite.config.ts has `usePolling: true`

### Complete Reset
```bash
# Stop and remove everything
./docker-control.sh clean

# Restart from scratch
./docker-control.sh start
```

## Production Deployment

For production, use production Dockerfiles:

```bash
# Build production images
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

# Start production services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

Production changes:
- Frontend: Nginx serves static files with SPA routing
- Backend: Uses Gunicorn instead of development server
- No hot reload or debug ports
- Optimized images and caching

## Data Persistence & Volume Management

### 🚨 CRITICAL DATA PERSISTENCE SOLUTION

**Problem**: Docker Desktop on Windows/WSL can lose all data when restarted, requiring complete re-seeding.

**Solution**: We use a backup/restore strategy with automated scripts that save data outside Docker's control.

### 📁 Persistence Scripts

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `backup-databases.sh` | Saves database data to local files | **Before stopping work** |
| `restore-databases.sh` | Restores data from backups | **After starting containers** |
| `init-databases.sh` | First-time database setup | **Initial setup only** |

### 🔄 Daily Workflow (Updated)

#### **Before Stopping Work (CRITICAL)**
```bash
# 1. Backup your data (NEVER SKIP THIS)
./backup-databases.sh

# 2. Now safe to stop containers
./docker-control.sh stop
```

#### **When Starting Work**
```bash
# 1. Start containers
./docker-control.sh start

# 2. Wait for containers to be healthy
./docker-control.sh status

# 3. If SuperTokens database is missing (common):
docker exec p2p-postgres psql -U postgres -c "CREATE DATABASE supertokens;"
docker restart p2p-supertokens

# 4. Restore your data from backup
./restore-databases.sh
```

### 🏗️ First Time Setup

```bash
# 1. Start all containers
./docker-control.sh start

# 2. Initialize databases and seed test data
./init-databases.sh

# 3. Create initial backup
./backup-databases.sh
```

### 📊 Backup Details

**What Gets Backed Up:**
- **PostgreSQL**: All databases including SuperTokens, organizations (17), users (25), forum categories (6)
- **MongoDB**: Use cases (15) and all document collections
- **Location**: `./database-backups/` directory (git-ignored)
- **Retention**: Last 5 backups are kept automatically

**Backup Files:**
```
database-backups/
├── postgres_backup_20250810_143022.sql
├── mongo_backup_20250810_143022.archive
└── ... (previous backups)
```

### 🔧 Common Issues & Solutions

#### **SuperTokens Won't Start**
```bash
# SuperTokens database always needs to be created after restart
docker exec p2p-postgres psql -U postgres -c "CREATE DATABASE supertokens;"
docker restart p2p-supertokens
./docker-control.sh status  # Verify it's running
```

#### **"Table doesn't exist" Errors**
```bash
# Create tables directly if migrations fail
docker exec p2p-backend python -c "
from app.db.session import engine
from app.models.base import BaseModel
import asyncio

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)
        
asyncio.run(create_tables())
"
```

#### **Want Fresh Data**
```bash
# Reset everything and re-seed
docker exec p2p-backend python scripts/seed_all.py reset
./backup-databases.sh  # Backup the fresh data
```

#### **No Backup Files Found**
```bash
# If restore fails due to missing backups, seed fresh data
./init-databases.sh
./backup-databases.sh  # Create backup for next time
```

### 🎯 Data Verification Commands

**Check Data After Restore:**
```bash
# PostgreSQL data counts
docker exec p2p-postgres psql -U postgres -d p2p_sandbox -c "
SELECT 'Organizations' as table_name, COUNT(*) as count FROM organizations
UNION ALL
SELECT 'Users', COUNT(*) FROM users;
"

# MongoDB data counts
docker exec p2p-mongodb mongosh p2p_sandbox --eval "
db.use_cases.countDocuments({})
"

# Expected counts after successful restore:
# Organizations: 17
# Users: 25  
# Use Cases: 15
```

### ⚠️ What NOT to Do

**NEVER run these commands** (they delete all data):
```bash
# ❌ These will delete ALL your data:
./docker-control.sh clean
docker-compose down -v
docker-compose down --volumes
docker volume prune
docker system prune -a --volumes
```

### 🔍 Troubleshooting Commands

```bash
# Check if volumes exist
docker volume ls | grep p2p-sandbox

# Check container status
./docker-control.sh status

# View database logs
./docker-control.sh logs postgres
./docker-control.sh logs mongodb

# Test database connectivity
docker exec p2p-postgres pg_isready -U postgres
docker exec p2p-mongodb mongosh --eval "db.adminCommand('ping')"

# Check backup files
ls -la ./database-backups/
```

---

### **Why This Persistence Solution?**

Docker Desktop on Windows/WSL has known issues where volumes can disappear when:
- Docker Desktop updates or restarts
- Windows reboots  
- WSL2 backend restarts
- Docker daemon resets

Our backup/restore approach works around this by storing data as regular files outside Docker's control.

### **Alternative Solutions Considered**

#### **Bind Mounts (Attempted)**
```yaml
# This was tried but failed due to WSL permission issues
volumes:
  postgres_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ./docker-volumes/postgres
```
**Result**: Permission errors on WSL, abandoned this approach.

#### **External Cloud Databases**  
**Pros**: Never lose data, managed backups
**Cons**: Cost, network latency, requires internet
**Recommendation**: Consider for production only

### **Future Improvements**

Consider these enhancements:
- Automated daily backups via cron job
- Cloud storage sync for backups (AWS S3, Google Drive)
- Database health monitoring and alerts
- Automated restore testing

---

## **CRITICAL REMINDERS** ⚠️

### **Commands That WILL DELETE ALL DATA**
**NEVER run these unless you want to lose everything:**
```bash
./docker-control.sh clean        # Deletes volumes
docker-compose down -v          # Deletes volumes
docker-compose down --volumes   # Deletes volumes
docker volume prune             # Deletes unused volumes
docker system prune -a --volumes # Deletes everything
```

### **Safe Daily Workflow Summary**
```bash
# ✅ SAFE - Start work
./docker-control.sh start
./restore-databases.sh

# ✅ SAFE - End work  
./backup-databases.sh
./docker-control.sh stop
```

**For detailed documentation on the persistence solution, see `DOCKER_DATA_PERSISTENCE.md`**
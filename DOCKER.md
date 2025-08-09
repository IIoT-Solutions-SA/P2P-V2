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

Start the entire application stack with a single command:

```bash
./docker-control.sh start
```

## Services

The following services run in Docker containers:

| Service | Container | Ports | Purpose |
|---------|-----------|-------|---------|
| Frontend | `p2p-frontend` | 5173 | React app with hot reload |
| Backend | `p2p-backend` | 8000, 5678 | FastAPI server + debug port |
| PostgreSQL | `p2p-postgres` | 5432 | Main database |
| MongoDB | `p2p-mongodb` | 27017 | Document storage |
| Redis | `p2p-redis` | 6379 | Caching and sessions |
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

## Volume Management & Troubleshooting

### Understanding Docker Volumes

The P2P Sandbox uses persistent volumes for data storage:

```yaml
volumes:
  postgres_data:    # PostgreSQL database files
  mongo_data:       # MongoDB database files  
  file_storage:     # User uploads and media files
```

### Volume Configuration Strategies

#### Development (Current Setup) ✅
```yaml
volumes:
  postgres_data:
    driver: local    # Docker manages automatically
```
**Pros:** Simple, automatic creation, easy cleanup
**Cons:** Data lost when volumes are explicitly deleted

#### Production with Named Volumes
```yaml
volumes:
  postgres_data:
    name: p2p-prod-postgres-${ENVIRONMENT:-staging}
    driver: local
```
**Pros:** Predictable names, easier backup/restore
**Cons:** Still local to single host

#### Production with External Volumes
```yaml
volumes:
  postgres_data:
    external: true
    name: p2p-prod-postgres-data  # Must exist before startup
```
**Pros:** Full control, supports shared storage
**Cons:** Requires manual volume creation

### Common Volume Issues & Solutions

#### Issue: "external volume not found"
```bash
# Error: external volume "p2p-backend-app_file_storage" not found
```

**Solution 1: Create missing volume**
```bash
docker volume create p2p-backend-app_file_storage
```

**Solution 2: Switch to local volumes (recommended for dev)**
```yaml
volumes:
  file_storage:
    driver: local  # Remove external: true
```

#### Issue: Data Loss After Container Cleanup
**Cause:** Volumes were deleted along with containers
**Prevention:**
```bash
# Safe cleanup (keeps volumes)
./docker-control.sh stop
docker container prune

# Dangerous cleanup (deletes volumes!)
./docker-control.sh clean  # ⚠️ This deletes ALL data
```

### Volume Health Checks

Add these checks to prevent startup issues:

```bash
# Check if volumes exist
docker volume ls | grep p2p

# Verify volume contents
docker run --rm -v p2p-sandbox_postgres_data:/data alpine ls -la /data

# Check volume size
docker system df -v
```

### Data Backup & Recovery

#### Backup Volumes
```bash
# PostgreSQL backup
docker exec p2p-postgres pg_dumpall -U postgres > backup.sql

# MongoDB backup  
docker exec p2p-mongodb mongodump --out /backup
docker cp p2p-mongodb:/backup ./mongodb-backup

# Volume-level backup (all data)
docker run --rm -v p2p-sandbox_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres-$(date +%Y%m%d).tar.gz /data
```

#### Restore Volumes
```bash
# PostgreSQL restore
cat backup.sql | docker exec -i p2p-postgres psql -U postgres

# MongoDB restore
docker cp ./mongodb-backup p2p-mongodb:/backup
docker exec p2p-mongodb mongorestore /backup

# Volume-level restore
docker run --rm -v p2p-sandbox_postgres_data:/data -v $(pwd):/backup alpine tar xzf /backup/postgres-20250809.tar.gz -C /
```

### Development Environment Reset

If you need a completely fresh environment:

```bash
# ⚠️ WARNING: This deletes all data
./docker-control.sh stop
./docker-control.sh clean

# Start fresh
./docker-control.sh start

# Re-seed databases
./docker-control.sh exec backend python scripts/seed_all.py
```

### Production Volume Recommendations

#### For Small Deployments (Single Server)
```yaml
volumes:
  postgres_data:
    name: p2p-prod-postgres-${ENVIRONMENT}
    driver: local
```

#### For High-Availability Deployments
```yaml
volumes:
  postgres_data:
    driver: nfs
    driver_opts:
      share: nfs-server:/path/to/postgres
```

#### For Cloud Deployments (AWS/Azure/GCP)
```yaml
volumes:
  postgres_data:
    driver: cloudstor:aws
    driver_opts:
      backing: ebs
      size: 20
```

### Monitoring Volume Health

Add to your monitoring stack:

```bash
# Volume usage alerts
docker system df --format "table {{.Type}}\t{{.TotalCount}}\t{{.Size}}\t{{.Reclaimable}}"

# Check volume mount status
docker inspect p2p-postgres | grep -A 10 "Mounts"

# Monitor database health
docker exec p2p-postgres pg_isready -U postgres
docker exec p2p-mongodb mongosh --eval "db.adminCommand('ping')"
```

### Environment-Specific Volume Configuration

Create different configurations for different environments:

#### docker-compose.dev.yml (Current)
```yaml
volumes:
  postgres_data:
    driver: local
```

#### docker-compose.staging.yml
```yaml
volumes:
  postgres_data:
    name: p2p-staging-postgres
    driver: local
```

#### docker-compose.prod.yml
```yaml
volumes:
  postgres_data:
    external: true
    name: p2p-prod-postgres-data
```

### Prevention Checklist

Before making volume changes:

- [ ] Backup existing data
- [ ] Test volume configuration in development
- [ ] Verify volume names match across environments
- [ ] Check disk space availability
- [ ] Document volume recovery procedures
- [ ] Test disaster recovery process

### Getting Help

If you encounter volume issues:

1. Check volume status: `docker volume ls`
2. Inspect volume details: `docker volume inspect <volume_name>`
3. Check container logs: `./docker-control.sh logs <service>`
4. Verify disk space: `docker system df`
5. Test with minimal setup first

---

## Data Safety & Loss Prevention ⚠️ CRITICAL

### **SAFE vs DANGEROUS Docker Operations**

#### ✅ **SAFE Operations (Data Preserved)**
```bash
# These commands preserve all data in volumes
./docker-control.sh stop          # Safe - stops containers, keeps volumes
./docker-control.sh start         # Safe - starts containers, volumes intact  
./docker-control.sh restart       # Safe - restart containers, volumes intact
docker-compose restart <service>  # Safe - restart single service
docker-compose down               # Safe - removes containers but keeps named volumes
```

#### ⚠️ **DANGEROUS Operations (Data Loss Risk)**
```bash
# ❌ NEVER run these commands unless you want to delete ALL data
./docker-control.sh clean         # DELETES VOLUMES - ALL DATA LOST!
docker-compose down -v            # DELETES VOLUMES - ALL DATA LOST! 
docker-compose down --volumes     # DELETES VOLUMES - ALL DATA LOST!
docker volume prune               # DELETES UNUSED VOLUMES - DATA LOST!
docker system prune -a --volumes  # DELETES EVERYTHING - ALL DATA LOST!

# ❌ Manual volume deletion - NEVER do this accidentally
docker volume rm p2p-sandbox_postgres_data
docker volume rm p2p-sandbox_mongo_data
```

### **Daily Startup/Shutdown Best Practices**

#### **Safe Application Startup Sequence**
```bash
# 1. Standard startup (safest)
./docker-control.sh start

# 2. If services are already running
./docker-control.sh status  # Check first
./docker-control.sh restart # Only if needed

# 3. If you need fresh containers but want to keep data
docker-compose down          # Remove containers only
./docker-control.sh start   # Start with existing volumes
```

#### **Safe Application Shutdown Sequence**
```bash
# 1. Standard shutdown (recommended)
./docker-control.sh stop

# 2. Alternative (also safe)
docker-compose down    # Removes containers but preserves volumes

# 3. Check volumes are still there after shutdown
docker volume ls | grep p2p-sandbox
```

### **Data Backup Strategies**

#### **Before Any Maintenance Operations**
```bash
# 1. Create database backups
./docker-control.sh exec backend python -c "
import asyncio
from datetime import datetime

async def backup():
    # PostgreSQL backup
    import subprocess
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    subprocess.run([
        'docker', 'exec', 'p2p-postgres', 
        'pg_dumpall', '-U', 'postgres'
    ], stdout=open(f'backup_postgres_{timestamp}.sql', 'w'))
    
    print(f'PostgreSQL backup created: backup_postgres_{timestamp}.sql')

asyncio.run(backup())
"

# 2. MongoDB backup
docker exec p2p-mongodb mongodump --out /backup
docker cp p2p-mongodb:/backup ./mongodb-backup-$(date +%Y%m%d_%H%M%S)

# 3. Volume-level backup (complete data protection)
timestamp=$(date +%Y%m%d_%H%M%S)
docker run --rm -v p2p-sandbox_postgres_data:/data -v $(pwd):/backup alpine \
    tar czf /backup/postgres-volume-backup-${timestamp}.tar.gz /data
    
docker run --rm -v p2p-sandbox_mongo_data:/data -v $(pwd):/backup alpine \
    tar czf /backup/mongo-volume-backup-${timestamp}.tar.gz /data
```

### **Volume Health Monitoring**

#### **Pre-Operation Checklist**
```bash
# Always run these before any Docker operations:

# 1. Check volume status
docker volume ls | grep p2p-sandbox
# Expected output: 3 volumes (postgres_data, mongo_data, file_storage)

# 2. Verify data exists
docker run --rm -v p2p-sandbox_postgres_data:/data alpine ls -la /data
docker run --rm -v p2p-sandbox_mongo_data:/data alpine ls -la /data

# 3. Check disk space
docker system df -v

# 4. Record current data counts (for verification after operations)
./docker-control.sh exec backend python -c "
import asyncio
import sqlalchemy as sa
from app.db.session import engine
from motor.motor_asyncio import AsyncIOMotorClient

async def count_data():
    async with engine.begin() as conn:
        result = await conn.execute(sa.text('SELECT COUNT(*) FROM organizations'))
        orgs = result.fetchone()[0]
        result = await conn.execute(sa.text('SELECT COUNT(*) FROM users'))
        users = result.fetchone()[0]
    
    client = AsyncIOMotorClient('mongodb://mongodb:27017')
    db = client.p2p_sandbox
    use_cases = await db.use_cases.count_documents({})
    client.close()
    
    print(f'BEFORE OPERATION - Orgs: {orgs}, Users: {users}, Use Cases: {use_cases}')

asyncio.run(count_data())
"
```

#### **Post-Operation Verification**
```bash
# After any Docker operation, verify data integrity:

# 1. Check services are healthy
./docker-control.sh status

# 2. Verify data counts match pre-operation counts
./docker-control.sh exec backend python -c "
import asyncio
import sqlalchemy as sa  
from app.db.session import engine
from motor.motor_asyncio import AsyncIOMotorClient

async def verify_data():
    async with engine.begin() as conn:
        result = await conn.execute(sa.text('SELECT COUNT(*) FROM organizations'))
        orgs = result.fetchone()[0]
        result = await conn.execute(sa.text('SELECT COUNT(*) FROM users'))
        users = result.fetchone()[0]
    
    client = AsyncIOMotorClient('mongodb://mongodb:27017')
    db = client.p2p_sandbox
    use_cases = await db.use_cases.count_documents({})
    client.close()
    
    print(f'AFTER OPERATION - Orgs: {orgs}, Users: {users}, Use Cases: {use_cases}')
    
    if orgs > 0 and users > 0:
        print('✅ Data integrity verified')
    else:
        print('❌ DATA LOSS DETECTED!')

asyncio.run(verify_data())
"

# 3. Test application functionality
curl -s http://localhost:8000/health | grep -q "healthy" && echo "✅ Backend healthy" || echo "❌ Backend issue"
curl -s http://localhost:5173 | grep -q "<title>" && echo "✅ Frontend healthy" || echo "❌ Frontend issue"
```

### **Emergency Data Recovery**

#### **If Data Loss Detected**
```bash
# 1. STOP all operations immediately
./docker-control.sh stop

# 2. Check if volumes still exist
docker volume ls | grep p2p-sandbox

# 3. If volumes exist but are empty, restore from backup
# PostgreSQL restore:
cat backup_postgres_TIMESTAMP.sql | docker exec -i p2p-postgres psql -U postgres

# MongoDB restore:
docker cp ./mongodb-backup-TIMESTAMP p2p-mongodb:/backup
docker exec p2p-mongodb mongorestore /backup

# 4. If volumes were deleted, recreate and restore
docker volume create p2p-sandbox_postgres_data
docker volume create p2p-sandbox_mongo_data
# Then restore from backups as above

# 5. Re-seed if no backups available
./docker-control.sh start
./docker-control.sh exec backend python scripts/seed_all.py
```

### **Common Data Loss Scenarios & Prevention**

#### **Scenario 1: Accidental Volume Deletion**
- **Cause**: Running `docker-compose down -v` or `./docker-control.sh clean`
- **Prevention**: Never use `-v` or `--volumes` flags unless you explicitly want to delete data
- **Recovery**: Restore from backup or re-seed

#### **Scenario 2: Volume Configuration Changes**
- **Cause**: Changing volume config from `local` to `external` without creating volumes
- **Prevention**: Always backup before configuration changes
- **Recovery**: Fix configuration and restore data

#### **Scenario 3: Disk Space Issues**
- **Cause**: Docker daemon purging volumes due to disk space
- **Prevention**: Monitor disk space with `docker system df`
- **Recovery**: Free space and restore from backup

#### **Scenario 4: Docker Daemon Reset**
- **Cause**: Docker Desktop reset or daemon corruption
- **Prevention**: Regular backups, use persistent volume locations
- **Recovery**: Restore from backup after daemon restart

### **Environment-Specific Recommendations**

#### **Development Environment**
```bash
# Daily startup routine
docker volume ls | grep p2p-sandbox  # Verify volumes exist
./docker-control.sh start            # Start application
# After startup, verify data counts

# Daily shutdown routine  
./docker-control.sh stop             # Safe shutdown
# Volumes remain for next startup
```

#### **Production Environment**
```bash
# Use external volumes with explicit names
volumes:
  postgres_data:
    external: true
    name: p2p-prod-postgres-data

# Automated backup schedule
0 2 * * * /path/to/backup-script.sh  # Daily 2 AM backups

# Volume monitoring
docker volume inspect p2p-prod-postgres-data | grep Mountpoint
du -sh /var/lib/docker/volumes/p2p-prod-postgres-data/
```

#### **Staging Environment**
```bash
# Named volumes for consistency
volumes:
  postgres_data:
    name: p2p-staging-postgres-${ENVIRONMENT}
    driver: local

# Weekly backup retention
find . -name "backup_*.sql" -mtime +7 -delete
```

### **Data Safety Checklist**

#### **Before ANY Docker Operation**
- [ ] Verify current data counts (run pre-operation check)
- [ ] Confirm disk space availability (`docker system df`)
- [ ] Create backup if making configuration changes
- [ ] Double-check command (no `-v` or `--volumes` flags)
- [ ] Test on staging environment first (if available)

#### **After ANY Docker Operation**
- [ ] Verify services are running (`./docker-control.sh status`)
- [ ] Check data integrity (run post-operation verification)
- [ ] Test application functionality (can access pages, data loads)
- [ ] Document any issues for future reference

#### **Weekly Maintenance**
- [ ] Create full database backups
- [ ] Monitor volume size growth
- [ ] Clean up old backup files (keep last 4 weeks)
- [ ] Update documentation with any new procedures

### **Emergency Contacts & Procedures**

#### **If Data Loss Occurs**
1. **STOP all operations immediately**
2. **Do not restart Docker or run any volume commands**
3. **Document exactly what commands were run**
4. **Check if volumes still exist with `docker volume ls`**
5. **Restore from most recent backup**
6. **If no backup exists, re-seed with `scripts/seed_all.py`**
7. **Update procedures to prevent recurrence**

---

## **CRITICAL REMINDER** ⚠️

**The following commands will DELETE ALL YOUR DATA:**
- `./docker-control.sh clean`
- `docker-compose down -v`
- `docker-compose down --volumes`  
- `docker volume prune`
- `docker system prune -a --volumes`

**NEVER run these commands unless you explicitly want to delete all data and have current backups!**

---

Remember: **Data safety first!** Always backup before making volume configuration changes in production.
# Complete Shutdown & Restart Guide for P2P Sandbox

## Overview
This guide provides the complete workflow for safely shutting down your entire development environment (including Docker Desktop and WSL) and restarting it while preserving all data.

## Complete Shutdown & Restart Workflow

### Phase 1: Application Shutdown

#### 1. Stop P2P Application Services
```bash
# Navigate to project root
cd /mnt/d/Projects/P2P-V2

# Stop all application containers gracefully
./docker-control.sh stop

# Verify all containers are stopped
docker ps -a
```

#### 2. Backup ALL Data (Critical - Preserves Dynamic Content)
**Important**: This backs up ALL data including new users, forum posts, use cases, and any content created during your development sessions.

```bash
# Create backup directory with timestamp
BACKUP_DIR="/mnt/d/Projects/P2P-V2/backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "🔄 Creating comprehensive backup of all data..."

# Export complete database data (includes ALL dynamic content)
echo "📊 Backing up PostgreSQL databases..."
docker-compose exec -T postgres pg_dump -U p2p_user p2p_sandbox > "$BACKUP_DIR/p2p_sandbox_complete.sql"
docker-compose exec -T postgres pg_dump -U supertokens supertokens > "$BACKUP_DIR/supertokens_complete.sql"

# Export MongoDB data (documents, files, etc.)
echo "📄 Backing up MongoDB collections..."
docker-compose exec mongodb mongodump --db p2p_mongodb --out /tmp/mongo_backup
docker cp $(docker-compose ps -q mongodb):/tmp/mongo_backup "$BACKUP_DIR/"

# Create complete Docker volume backups (preserves all filesystem data)
echo "💾 Creating Docker volume backups..."
docker run --rm -v p2p-backend-app_postgres_data:/data -v "$BACKUP_DIR":/backup alpine tar czf /backup/postgres_volume_complete.tar.gz -C /data .
docker run --rm -v p2p-backend-app_mongodb_data:/data -v "$BACKUP_DIR":/backup alpine tar czf /backup/mongodb_volume_complete.tar.gz -C /data .
docker run --rm -v p2p-backend-app_redis_data:/data -v "$BACKUP_DIR":/backup alpine tar czf /backup/redis_volume_complete.tar.gz -C /data .

# Create data summary for verification
echo "📋 Creating data summary..."
./docker-control.sh exec backend python -c "
from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.models.organization import Organization
from app.models.forum import ForumTopic, ForumPost
from sqlalchemy import select, func
import asyncio

async def create_summary():
    async with AsyncSessionLocal() as session:
        user_count = await session.execute(select(func.count(User.id)))
        org_count = await session.execute(select(func.count(Organization.id)))
        topic_count = await session.execute(select(func.count(ForumTopic.id)))
        post_count = await session.execute(select(func.count(ForumPost.id)))
        
        summary = f'''
BACKUP SUMMARY - $(date)
================================
Users: {user_count.scalar()}
Organizations: {org_count.scalar()}
Forum Topics: {topic_count.scalar()}
Forum Posts: {post_count.scalar()}

This backup includes ALL data:
- Initial seeded data
- All users created during development
- All forum posts and topics
- All use cases and submissions
- All authentication records
        '''
        print(summary)

asyncio.run(create_summary())
" > "$BACKUP_DIR/backup_summary.txt"

echo "✅ Complete backup finished in: $BACKUP_DIR"
echo "📊 This backup preserves ALL your development work including:"
echo "   - Initial seeded data"
echo "   - New users created via registration"
echo "   - Forum topics and posts"
echo "   - Use case submissions"
echo "   - All authentication data"
```

### Phase 2: Docker Desktop Shutdown

#### 3. Stop All Docker Containers
```bash
# Stop all running containers
docker stop $(docker ps -q) 2>/dev/null || echo "No containers to stop"

# Verify no containers are running
docker ps
```

#### 4. Close Docker Desktop
```bash
# Option A: Command line (if available)
wsl.exe --shutdown

# Option B: Manual
# - Right-click Docker Desktop system tray icon
# - Select "Quit Docker Desktop"
# - Wait for Docker Desktop to fully close
```

### Phase 3: WSL Shutdown

#### 5. Exit WSL and Shutdown
```bash
# From within WSL, exit all terminals
exit

# From Windows Command Prompt or PowerShell:
wsl --shutdown

# Verify WSL is shut down
wsl --list --verbose
# (Should show all distributions as "Stopped")
```

### Phase 4: System Restart

#### 6. Restart Your PC
```bash
# From Windows Command Prompt (as Administrator) or manually restart
shutdown /r /t 0
```

---

## Complete Startup Workflow

### Phase 1: System Startup

#### 1. Start Docker Desktop
- **Manual**: Launch Docker Desktop from Windows Start Menu
- **Automatic**: If configured to start with Windows
- **Verification**: Wait for Docker Desktop to show "Engine running" status

#### 2. Verify Docker Engine
```bash
# Open PowerShell or Command Prompt
docker --version
docker info
```

### Phase 2: WSL Initialization

#### 3. Start WSL Environment
```bash
# From Windows Command Prompt/PowerShell
wsl -d Ubuntu  # or your WSL distribution name

# Or simply open Windows Terminal with WSL profile
```

#### 4. Navigate to Project Directory
```bash
cd /mnt/d/Projects/P2P-V2

# Verify project files are intact
ls -la
```

### Phase 3: Application Startup

#### 5. Start P2P Application Stack
```bash
# Start entire application stack
./docker-control.sh start

# Monitor startup progress
./docker-control.sh status
```

#### 6. Verify All Services
```bash
# Check container health
docker ps

# Test service endpoints
curl http://localhost:8000/health
curl http://localhost:5173

# Check database connections
./docker-control.sh exec backend python -c "
from app.db.session import AsyncSessionLocal
import asyncio

async def test_db():
    async with AsyncSessionLocal() as session:
        result = await session.execute('SELECT 1')
        print('✅ PostgreSQL connected')

asyncio.run(test_db())
"
```

### Phase 4: Complete Data Verification

#### 7. Verify All Data Types Are Preserved
**Important**: This includes both initial seeded data AND all new content created during development sessions (new users, use cases, forum posts, etc.)

```bash
# Comprehensive data integrity check
./docker-control.sh exec backend python -c "
from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.models.organization import Organization
from app.models.forum import ForumTopic, ForumPost
from sqlalchemy import select, func
import asyncio

async def check_all_data():
    async with AsyncSessionLocal() as session:
        # Check users (both seeded and newly created)
        user_count = await session.execute(select(func.count(User.id)))
        user_total = user_count.scalar()
        print(f'✅ Users: {user_total} total')
        
        # Check organizations
        org_count = await session.execute(select(func.count(Organization.id)))
        org_total = org_count.scalar()
        print(f'✅ Organizations: {org_total} total')
        
        # Check forum content (including new posts/topics created during development)
        topic_count = await session.execute(select(func.count(ForumTopic.id)))
        topic_total = topic_count.scalar()
        print(f'✅ Forum Topics: {topic_total} total')
        
        post_count = await session.execute(select(func.count(ForumPost.id)))
        post_total = post_count.scalar()
        print(f'✅ Forum Posts: {post_total} total')
        
        # Show recent activity (to verify new data is preserved)
        recent_users = await session.execute(
            select(User.email, User.created_at)
            .order_by(User.created_at.desc())
            .limit(5)
        )
        print(f'\\n📋 Most Recent Users:')
        for user in recent_users:
            print(f'  - {user.email} (created: {user.created_at})')
        
        recent_topics = await session.execute(
            select(ForumTopic.title, ForumTopic.created_at)
            .order_by(ForumTopic.created_at.desc())
            .limit(3)
        )
        print(f'\\n📋 Most Recent Forum Topics:')
        for topic in recent_topics:
            print(f'  - {topic.title} (created: {topic.created_at})')

asyncio.run(check_all_data())
"

# Check SuperTokens authentication data (includes all registered users)
./docker-control.sh exec backend python -c "
from supertokens_python.recipe.emailpassword.asyncio import get_users_oldest_first
from app.core.supertokens import init_supertokens
import asyncio

async def check_supertokens():
    init_supertokens()
    users = await get_users_oldest_first('public', limit=100)  # Get more to see all users
    print(f'✅ SuperTokens: {len(users.users)} authenticated users')
    
    # Show recent SuperTokens users
    print(f'\\n📋 SuperTokens Users:')
    for user in users.users[:5]:  # Show first 5
        print(f'  - {user.email} (ID: {user.user_id[:8]}...)')

asyncio.run(check_supertokens())
"

# Check MongoDB data (if using for documents/files)
./docker-control.sh exec mongodb mongosh p2p_mongodb --eval "
print('✅ MongoDB Collections:');
db.getCollectionNames().forEach(function(collection) {
    var count = db.getCollection(collection).countDocuments();
    print('  - ' + collection + ': ' + count + ' documents');
});
"
```

#### 8. Test Authentication Flow
```bash
# Test login with a known user
curl -X POST http://localhost:8000/auth/signin \
  -H "Content-Type: application/json" \
  -d '{
    "formFields": [
      {"id": "email", "value": "sarah.ahmed@advanced-electronics.sa"},
      {"id": "password", "value": "TestPassword123!"}
    ]
  }'
```

---

## Complete Data Persistence Strategy

### What Data Persists Across Restarts

#### ✅ ALL Dynamic Content is Preserved
1. **User Data**
   - Initial seeded users (26 users from seed script)
   - New users registered during development sessions
   - User profiles, preferences, and settings
   - Authentication data (SuperTokens users)

2. **Forum Content**
   - Initial forum topics and categories
   - New topics created during development
   - All forum posts and replies
   - User interactions and votes

3. **Use Cases & Business Content**
   - Initial seeded use cases
   - New use case submissions
   - File uploads and attachments
   - Comments and feedback

4. **System Data**
   - Organization information
   - User roles and permissions
   - Session data and active logins
   - Application settings and configurations

### Why This Works (Technical Details)
1. **Docker Named Volumes**: All critical data is stored in named Docker volumes that persist independently of containers
2. **Volume Persistence**: Docker volumes are stored in WSL2 virtual disk, surviving container stops/starts
3. **WSL2 Virtual Disk**: Virtual disks are stored in Windows filesystem and persist across WSL shutdowns
4. **Windows File System**: Volume data survives PC restarts as it's stored on the Windows host

### Critical Data Locations & What They Contain
```bash
# PostgreSQL Data - Contains ALL business data
Volume: p2p-backend-app_postgres_data
Location: /var/lib/docker/volumes/p2p-backend-app_postgres_data/_data
Contains:
  - users table (seeded + new registrations)
  - organizations table
  - forum_topics and forum_posts tables  
  - use_cases and file_metadata tables
  - all foreign key relationships

# SuperTokens Database - Contains ALL authentication data
Volume: p2p-backend-app_postgres_data (same volume, different database)
Database: supertokens
Contains:
  - emailpassword_users (all login accounts)
  - session_info (active sessions)
  - password_reset_tokens
  - email_verification_tokens

# MongoDB Data - Contains document storage
Volume: p2p-backend-app_mongodb_data
Location: /var/lib/docker/volumes/p2p-backend-app_mongodb_data/_data
Contains:
  - File uploads and binary data
  - Extended use case content
  - Search indexes and analytics

# Redis Data - Contains cached data and sessions
Volume: p2p-backend-app_redis_data
Location: /var/lib/docker/volumes/p2p-backend-app_redis_data/_data
Contains:
  - Session cache
  - API response cache
  - Background job queues
```

### Backup/Restore Strategy

#### Creating Backups
```bash
# Automated backup script (run before shutdown)
#!/bin/bash
BACKUP_DIR="/mnt/d/Projects/P2P-V2/backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Database dumps
docker-compose exec -T postgres pg_dump -U p2p_user p2p_sandbox > "$BACKUP_DIR/p2p_sandbox.sql"
docker-compose exec -T postgres pg_dump -U supertokens supertokens > "$BACKUP_DIR/supertokens.sql"

# Volume backups
docker run --rm -v p2p-backend-app_postgres_data:/data -v "$BACKUP_DIR":/backup alpine tar czf /backup/postgres_volume.tar.gz -C /data .
docker run --rm -v p2p-backend-app_mongodb_data:/data -v "$BACKUP_DIR":/backup alpine tar czf /backup/mongodb_volume.tar.gz -C /data .

echo "Backup completed: $BACKUP_DIR"
```

#### Restoring from Backup (if needed)
```bash
# Restore PostgreSQL database
docker-compose exec -T postgres psql -U p2p_user p2p_sandbox < "/path/to/backup/p2p_sandbox.sql"
docker-compose exec -T postgres psql -U supertokens supertokens < "/path/to/backup/supertokens.sql"

# Restore Docker volumes (if corrupted)
docker volume create p2p-backend-app_postgres_data
docker run --rm -v p2p-backend-app_postgres_data:/data -v "/path/to/backup":/backup alpine tar xzf /backup/postgres_volume.tar.gz -C /data
```

---

## Troubleshooting Common Issues

### Issue: Docker Desktop Won't Start
**Solution:**
```bash
# Restart Docker service
net stop com.docker.service
net start com.docker.service

# Or reset Docker Desktop
# Settings > Troubleshoot > Reset to factory defaults
```

### Issue: WSL Won't Start
**Solution:**
```bash
# From Windows Command Prompt (as Admin)
wsl --shutdown
wsl --unregister Ubuntu  # Only if necessary
wsl --install -d Ubuntu  # Reinstall if needed
```

### Issue: Data Appears Missing
**Solution:**
```bash
# Check if volumes exist
docker volume ls | grep p2p-backend-app

# Inspect volume contents
docker run --rm -v p2p-backend-app_postgres_data:/data alpine ls -la /data

# Restore from backup if necessary
```

### Issue: Containers Won't Start
**Solution:**
```bash
# Check Docker daemon
docker info

# Rebuild containers
./docker-control.sh stop
docker system prune -f
./docker-control.sh build
./docker-control.sh start
```

### Issue: Port Conflicts
**Solution:**
```bash
# Check what's using ports
netstat -tulpn | grep :8000
netstat -tulpn | grep :5432

# Kill conflicting processes
sudo kill -9 <PID>
```

---

## Quick Reference Commands

### Shutdown Sequence
```bash
# 1. Stop application
cd /mnt/d/Projects/P2P-V2 && ./docker-control.sh stop

# 2. Stop all Docker containers
docker stop $(docker ps -q) 2>/dev/null

# 3. Quit Docker Desktop (manual or command)
wsl --shutdown

# 4. Restart PC (manual)
shutdown /r /t 0
```

### Startup Sequence
```bash
# 1. Start Docker Desktop (manual or automatic)

# 2. Open WSL terminal
wsl -d Ubuntu

# 3. Navigate and start
cd /mnt/d/Projects/P2P-V2
./docker-control.sh start

# 4. Verify services
curl http://localhost:8000/health && curl http://localhost:5173
```

### Emergency Data Recovery
```bash
# Create emergency backup before major changes
docker run --rm -v p2p-backend-app_postgres_data:/source -v /mnt/d/emergency_backup:/backup alpine tar czf /backup/emergency_postgres_$(date +%Y%m%d_%H%M%S).tar.gz -C /source .
```

---

## Best Practices

1. **Regular Backups**: Create backups before major changes or system restarts
2. **Gradual Shutdown**: Always stop applications before stopping Docker
3. **Verify Status**: Check service health after each startup phase
4. **Monitor Logs**: Watch container logs during startup for errors
5. **Test Authentication**: Verify login functionality after restart

## Resources

- **Docker Documentation**: Volume management and container lifecycle
- **WSL2 Documentation**: Windows Subsystem for Linux best practices  
- **P2P Project Documentation**: `/DOCKER.md` for detailed container management
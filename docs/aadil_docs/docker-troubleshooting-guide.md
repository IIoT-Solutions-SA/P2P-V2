# Docker Container Troubleshooting Guide

## Overview
This guide documents common Docker container startup issues encountered during P2P Sandbox backend development and their solutions.

## Issue 1: Pydantic Settings CORS Parsing Error

### Problem
```
pydantic_settings.sources.SettingsError: error parsing value for field "BACKEND_CORS_ORIGINS" from source "DotEnvSettingsSource"
json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
```

### Root Cause
Pydantic Settings v2 automatically tries to parse List fields as JSON from environment variables, causing issues with comma-separated strings.

### Solution
Changed from List field to string field with a property for parsing:

```python
# Before (causes error)
BACKEND_CORS_ORIGINS: List[str] = []

# After (works correctly)
BACKEND_CORS_ORIGINS: str = ""

@property
def cors_origins(self) -> List[str]:
    """Get CORS origins as a list."""
    return parse_cors(self.BACKEND_CORS_ORIGINS)
```

### Files Modified
- `/app/core/config.py` - Changed CORS field type
- `/app/main.py` - Updated to use `settings.cors_origins` property

## Issue 2: MongoDB AsyncMongoClient Import Error

### Problem
```
ImportError: cannot import name 'AsyncMongoClient' from 'pymongo'
```

### Root Cause
PyMongo's AsyncMongoClient was moved/deprecated. Motor should be used for async MongoDB operations.

### Solution
```python
# Before (incorrect)
from pymongo import AsyncMongoClient

# After (correct)
from motor.motor_asyncio import AsyncIOMotorClient
```

### Files Modified
- `/app/db/session.py` - Updated MongoDB client imports

## Issue 3: SQL Execution Error - Cannot Execute Raw SQL String

### Problem
```
sqlalchemy.exc.ArgumentError: Textual SQL expression 'SELECT 1' should be explicitly declared as text('SELECT 1')
```

### Root Cause
SQLAlchemy 2.0 requires explicit text() wrapper for raw SQL strings for security reasons.

### Solution
```python
# Before (causes error)
await conn.execute("SELECT 1")

# After (works correctly)
from sqlalchemy import text
await conn.execute(text("SELECT 1"))
```

### Files Modified
- `/app/db/session.py` - Added text() wrapper for health check queries

## Issue 4: SQLModel Field Definition Conflicts

### Problem
```
RuntimeError: Field 'field_name' has conflict with protected namespace 'model_'.
ValueError: cannot specify both default and default_factory
```

### Root Cause
SQLModel has specific rules about field definitions:
1. Cannot use both `nullable` parameter and `sa_column` with nullable
2. Field names cannot conflict with SQLModel's protected namespaces
3. Cannot use both `default` and `default_factory`

### Solution
```python
# Before (causes error)
field: Optional[str] = Field(nullable=True, sa_column=Column(String, nullable=True))

# After (works correctly)
field: Optional[str] = Field(sa_column=Column(String, nullable=True))

# For defaults, use only one approach:
created_at: datetime = Field(default_factory=datetime.utcnow)  # Not both default= and default_factory=
```

### Files Modified
- `/app/models/user.py` - Fixed field definitions
- `/app/models/organization.py` - Fixed field definitions

## Issue 5: Missing Python Package in Running Container

### Problem
```
ModuleNotFoundError: No module named 'pythonjsonlogger'
```

### Root Cause
New Python dependencies added to requirements.txt but container not rebuilt.

### Solution
```bash
# Option A: Quick fix - install in running container (temporary)
docker exec p2p-backend pip install python-json-logger==2.0.7

# Option B: Proper fix - rebuild container (permanent)
docker-compose build backend
docker-compose up -d backend
```

### Best Practice
Always rebuild containers after adding new dependencies to requirements.txt

## Issue 6: Docker Container Not Picking Up Code Changes

### Problem
Container keeps using old code despite file changes due to volume mounting and caching.

### Solution Steps
1. **Restart container** (picks up changes if volume mounted correctly):
   ```bash
   docker-compose restart backend
   ```

2. **Force recreate if restart doesn't work**:
   ```bash
   docker-compose stop backend
   docker-compose rm -f backend
   docker-compose up -d backend
   ```

3. **Rebuild if code is cached**:
   ```bash
   docker-compose down backend
   docker-compose build backend
   docker-compose up -d backend
   ```

## Debugging Commands

### 1. Check Container Status
```bash
docker-compose ps
```

### 2. View Container Logs
```bash
# Full logs
docker logs p2p-backend

# Last 50 lines
docker logs p2p-backend --tail 50

# Follow logs in real-time
docker logs -f p2p-backend

# Search for errors
docker logs p2p-backend 2>&1 | grep -i error
```

### 3. Check Environment Variables in Container
```bash
# Check specific env var
docker exec p2p-backend printenv BACKEND_CORS_ORIGINS

# Check all env vars
docker exec p2p-backend printenv

# Check .env file in container
docker exec p2p-backend cat /app/.env
```

### 4. Test API Health
```bash
# From host
curl http://localhost:8000/health

# With more details
curl -v http://localhost:8000/health

# Pretty print JSON response
curl http://localhost:8000/health | python -m json.tool
```

### 5. Access Container Shell
```bash
# Interactive shell
docker exec -it p2p-backend /bin/bash

# Run Python commands
docker exec p2p-backend python -c "from app.core.config import settings; print(settings.BACKEND_CORS_ORIGINS)"
```

## Common Environment Variable Issues

### Empty Values
Empty values in .env file can cause JSON parsing errors:
```bash
# Find empty env vars
grep '=$' .env

# Common problematic empty values:
SUPERTOKENS_API_KEY=
SMTP_USER=
SMTP_PASSWORD=
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
SENTRY_DSN=
```

### Solution
Either provide values or ensure your config handles empty strings properly.

## Docker Compose Tips

### 1. Volume Mounting
Ensure your docker-compose.yml has proper volume mounting:
```yaml
volumes:
  - ./:/app  # Mounts current directory to /app in container
  - /app/__pycache__  # Prevents pycache conflicts
  - /app/.pytest_cache
```

### 2. Environment Variables
Can be set multiple ways:
```yaml
environment:
  - DATABASE_URL=postgresql+asyncpg://...  # Direct in compose
env_file:
  - .env  # From .env file
```

### 3. Dependencies
Ensure services start in correct order:
```yaml
depends_on:
  postgres:
    condition: service_healthy  # Waits for health check
  mongodb:
    condition: service_healthy
```

## Testing Configuration Locally

Create a test script to verify configuration:
```python
# test_config.py
import os
from dotenv import load_dotenv
load_dotenv()

try:
    from app.core.config import settings
    print("✅ Config loaded successfully!")
    print(f"CORS Origins: {settings.cors_origins}")
    print(f"Database URL: {settings.DATABASE_URL}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
```

Run with:
```bash
source venv/bin/activate
python test_config.py
```

## Prevention Strategies

1. **Always test configuration changes locally** before containerizing
2. **Use simple types** for environment variables (strings, not complex types)
3. **Add config validation** that provides clear error messages
4. **Document all environment variables** in .env.example
5. **Use health checks** to verify services are ready
6. **Monitor logs** during development for early error detection

## Quick Checklist When Backend Won't Start

- [ ] Check Docker Desktop is running (Windows/Mac)
- [ ] All required containers are up: `docker-compose ps`
- [ ] No port conflicts: `lsof -i :8000`
- [ ] Environment variables are set correctly
- [ ] Database containers are healthy
- [ ] Latest code changes are in container
- [ ] No Python import errors in logs
- [ ] CORS origins are properly formatted
- [ ] All required Python packages installed

## Getting Help

1. Check logs first: `docker logs p2p-backend`
2. Verify environment: `docker exec p2p-backend printenv`
3. Test imports: `docker exec p2p-backend python -c "from app.main import app"`
4. Check database connections
5. Verify file permissions in container

## Issue 7: SuperTokens Health Check Failing

### Problem
SuperTokens container health check fails because curl/nc tools are not available in the container.

### Temporary Solution
Changed health check from `service_healthy` to `service_started` in docker-compose.yml:
```yaml
depends_on:
  supertokens:
    condition: service_started  # Changed from service_healthy
```

### Permanent Solution (TODO)
Implement proper health check for SuperTokens in Phase 2.

## Comprehensive Docker Troubleshooting Workflow

When encountering Docker issues, follow this systematic approach:

### 1. Initial Diagnosis
```bash
# Check all container statuses
docker-compose ps

# Check specific container logs
docker-compose logs --tail=50 backend

# Check for Python errors
docker-compose logs backend | grep -i "error\|exception\|traceback"
```

### 2. Common Fix Attempts (in order)
```bash
# Level 1: Restart (for code changes)
docker-compose restart backend

# Level 2: Recreate (for config changes)
docker-compose up -d --force-recreate backend

# Level 3: Rebuild (for dependency changes)
docker-compose build --no-cache backend
docker-compose up -d backend

# Level 4: Full reset
docker-compose down
docker system prune -f
docker-compose up -d
```

### 3. Debugging Inside Container
```bash
# Test imports manually
docker exec p2p-backend python -c "from app.main import app; print('✅ Import successful')"

# Check installed packages
docker exec p2p-backend pip list | grep package-name

# Run specific module
docker exec p2p-backend python -m app.main
```

### 4. Environment Debugging
```bash
# Compare .env with container environment
diff <(sort .env) <(docker exec p2p-backend printenv | sort)

# Test specific config values
docker exec p2p-backend python -c "from app.core.config import settings; print(settings.dict())"
```

## Docker Build Optimization Tips

### 1. Use Build Cache Effectively
```dockerfile
# Copy requirements first (changes less frequently)
COPY requirements.txt .
RUN pip install -r requirements.txt

# Then copy code (changes frequently)
COPY . .
```

### 2. Speed Up Builds
```bash
# Use buildkit for faster builds
DOCKER_BUILDKIT=1 docker-compose build backend

# Use cache mount for pip
# Add to Dockerfile:
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt
```

### 3. Debug Build Issues
```bash
# Build with verbose output
docker-compose build --progress=plain backend

# Build specific stage
docker build --target development -t p2p-backend:dev .
```

## Phase 1 Specific Issues Summary

During Phase 1 implementation, we encountered and solved:

1. **Pydantic CORS parsing** - Changed List[str] to str with property
2. **MongoDB imports** - Switched to motor.motor_asyncio.AsyncIOMotorClient
3. **SQL execution** - Added text() wrapper for raw SQL
4. **SQLModel fields** - Removed conflicting nullable parameters
5. **Missing packages** - Rebuilt container after requirements.txt changes
6. **SuperTokens health** - Temporarily disabled health check

All issues were resolved and documented for future reference.

## Claude Code Environment Setup

### Headless Mode Benefits
During Phase 1 implementation, using Claude Code in "headless mode" provided significant advantages for Docker troubleshooting:

- **Direct Docker Command Execution**: Ability to run `docker-compose` commands directly
- **Real-time Container Debugging**: Live access to logs and container status
- **System-level Access**: Can test APIs with `curl`, check processes, etc.
- **Persistent Shell Session**: Maintains context across multiple commands

### Key Difference
- **Without Headless Mode**: Limited system access, may need manual command execution
- **With Headless Mode**: Full terminal access, can debug containers in real-time

### Setup
*TODO: Document specific headless mode setup steps for future reference*

## Environment Requirements for Docker Troubleshooting

1. **Docker Desktop Running** (Windows/Mac) or Docker daemon (Linux)
2. **Claude Code with System Access** (headless mode recommended)
3. **Proper User Permissions** for Docker commands
4. **Network Access** to container ports (8000, 5432, 27017, etc.)
5. **File System Access** to project directory

This guide should help resolve most Docker container startup issues. Update this document when encountering new issues and their solutions.
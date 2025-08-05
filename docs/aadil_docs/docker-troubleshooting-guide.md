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

## Issue 3: Docker Container Not Picking Up Code Changes

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

This guide should help resolve most Docker container startup issues. Update this document when encountering new issues and their solutions.
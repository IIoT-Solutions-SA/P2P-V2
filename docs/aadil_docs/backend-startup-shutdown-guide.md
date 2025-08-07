# P2P Backend Startup & Shutdown Guide

## Overview

This guide provides comprehensive steps to reliably start and stop the P2P Sandbox backend, avoiding common issues that cause startup failures. Follow these steps exactly to ensure consistent backend operation.

## Quick Reference

### ✅ Backend Startup Checklist
```bash
# 1. Navigate to backend directory
cd /mnt/d/Projects/P2P-V2/p2p-backend-app

# 2. Check for running processes
ps aux | grep uvicorn
curl -s http://localhost:8000/health || echo "No backend running"

# 3. Activate virtual environment
source venv/bin/activate

# 4. Verify dependencies
pip list | grep -E "(fastapi|sqlmodel|asyncpg|aiofiles|Pillow)"

# 5. Check database connections
docker-compose ps

# 6. Start backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --timeout-keep-alive 30

# 7. Verify startup
curl -s http://localhost:8000/health | python3 -m json.tool
```

### ⚠️ Backend Shutdown Checklist
```bash
# 1. Graceful shutdown (if running in foreground)
# Press Ctrl+C

# 2. Kill any background processes
pkill -f uvicorn
ps aux | grep uvicorn  # Verify no processes remain

# 3. Check port is free
lsof -i :8000 || echo "Port 8000 is free"

# 4. Optional: Stop databases
docker-compose stop
```

---

## Detailed Startup Procedure

### Step 1: Pre-Startup Environment Check

#### 1.1 Navigate to Backend Directory
```bash
cd /mnt/d/Projects/P2P-V2/p2p-backend-app
pwd  # Should show: /mnt/d/Projects/P2P-V2/p2p-backend-app
```

#### 1.2 Check for Existing Backend Processes
```bash
# Check if backend is already running
curl -s http://localhost:8000/health && echo "✅ Backend already running" && exit 0

# Check for zombie processes
ps aux | grep uvicorn
if [ $? -eq 0 ]; then
    echo "⚠️ Found existing uvicorn processes - kill them first"
    pkill -f uvicorn
    sleep 2
fi
```

#### 1.3 Verify Port Availability
```bash
# Ensure port 8000 is free
lsof -i :8000
if [ $? -eq 0 ]; then
    echo "❌ Port 8000 is occupied. Kill the process or use a different port."
    exit 1
fi
```

### Step 2: Environment Setup

#### 2.1 Activate Virtual Environment
```bash
# Check if venv exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Create it first:"
    echo "python3 -m venv venv"
    exit 1
fi

# Activate venv
source venv/bin/activate

# Verify activation
which python  # Should show path with 'venv'
```

#### 2.2 Verify Critical Dependencies
```bash
# Check for required packages
echo "🔍 Checking critical dependencies..."

REQUIRED_PACKAGES=(
    "fastapi==0.104.1"
    "sqlmodel==0.0.14" 
    "asyncpg==0.29.0"
    "aiofiles==24.1.0"
    "Pillow==10.1.0"
    "python-magic==0.4.27"
)

for package in "${REQUIRED_PACKAGES[@]}"; do
    pkg_name=$(echo $package | cut -d'=' -f1)
    if ! pip show $pkg_name > /dev/null 2>&1; then
        echo "❌ Missing package: $package"
        echo "Installing..."
        pip install $package
    else
        echo "✅ Found: $pkg_name"
    fi
done
```

#### 2.3 Environment Variables Check
```bash
# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️ .env file not found. Backend will use defaults."
    echo "Consider creating .env from .env.example if needed."
fi

# Verify DATABASE_URL format
if [ -f ".env" ]; then
    if grep -q "DATABASE_URL" .env; then
        echo "✅ DATABASE_URL found in .env"
    else
        echo "⚠️ DATABASE_URL not found in .env - using defaults"
    fi
fi
```

### Step 3: Database Verification

#### 3.1 Check Database Services
```bash
# Check if Docker services are running
echo "🗄️ Checking database services..."

# Check PostgreSQL
if docker-compose ps | grep -q "postgres.*Up"; then
    echo "✅ PostgreSQL service running"
else
    echo "⚠️ PostgreSQL service not running - starting..."
    docker-compose up -d postgres
    sleep 5
fi

# Check MongoDB
if docker-compose ps | grep -q "mongodb.*Up"; then
    echo "✅ MongoDB service running"  
else
    echo "⚠️ MongoDB service not running - starting..."
    docker-compose up -d mongodb
    sleep 5
fi

# Wait for services to be ready
echo "⏳ Waiting for databases to be ready..."
sleep 10
```

#### 3.2 Test Database Connections
```bash
# Test PostgreSQL connection
python3 -c "
import asyncio
import asyncpg
async def test_pg():
    try:
        conn = await asyncpg.connect('postgresql://postgres:password@localhost:5432/p2p_sandbox')
        await conn.close()
        print('✅ PostgreSQL connection successful')
    except Exception as e:
        print(f'❌ PostgreSQL connection failed: {e}')
        exit(1)
asyncio.run(test_pg())
" || echo "❌ PostgreSQL connection test failed"

# Test MongoDB connection
python3 -c "
import motor.motor_asyncio
import asyncio
async def test_mongo():
    try:
        client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://localhost:27017')
        await client.admin.command('ismaster')
        print('✅ MongoDB connection successful')
    except Exception as e:
        print(f'❌ MongoDB connection failed: {e}')
        exit(1)
asyncio.run(test_mongo())
" || echo "❌ MongoDB connection test failed"
```

### Step 4: Backend Startup

#### 4.1 Pre-startup Model Validation
```bash
# Quick model validation to catch SQLModel issues early
echo "🔍 Validating models..."
python3 -c "
try:
    from app.models.base import BaseModel
    from app.models.user import User
    from app.models.organization import Organization
    from app.models import FileMetadata
    print('✅ All models imported successfully')
except Exception as e:
    print(f'❌ Model import failed: {e}')
    exit(1)
" || (echo "❌ Model validation failed - check SQLModel definitions" && exit 1)
```

#### 4.2 Start Backend Server
```bash
echo "🚀 Starting backend server..."

# Start with comprehensive logging
uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload \
    --timeout-keep-alive 30 \
    --log-level info \
    --access-log &

# Store PID for later reference
BACKEND_PID=$!
echo $BACKEND_PID > .backend.pid

echo "Backend started with PID: $BACKEND_PID"
```

#### 4.3 Startup Verification
```bash
# Wait for server to start
echo "⏳ Waiting for backend to start..."
sleep 5

# Test health endpoint
MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s http://localhost:8000/health > /dev/null; then
        echo "✅ Backend health check passed"
        break
    else
        echo "⏳ Waiting for backend... ($((RETRY_COUNT + 1))/$MAX_RETRIES)"
        sleep 2
        ((RETRY_COUNT++))
    fi
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "❌ Backend failed to start within timeout"
    exit 1
fi
```

#### 4.4 Comprehensive API Testing
```bash
echo "🧪 Running comprehensive API tests..."

# Test core endpoints
ENDPOINTS=(
    "/health"
    "/api/v1/users/me"
    "/api/v1/organizations/me"
    "/api/v1/users/organization"
    "/api/v1/organizations/stats"
)

for endpoint in "${ENDPOINTS[@]}"; do
    response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000$endpoint)
    if [ "$response" = "200" ]; then
        echo "✅ $endpoint"
    else
        echo "⚠️ $endpoint (HTTP $response)"
    fi
done

echo "🎉 Backend startup complete!"
echo "📍 Backend available at: http://localhost:8000"
echo "📚 API docs at: http://localhost:8000/docs"
```

---

## Detailed Shutdown Procedure

### Step 1: Graceful Shutdown

#### 1.1 Stop Backend Process
```bash
echo "🛑 Stopping backend..."

# If running in foreground, use Ctrl+C
# If running in background, use PID
if [ -f ".backend.pid" ]; then
    BACKEND_PID=$(cat .backend.pid)
    kill -TERM $BACKEND_PID 2>/dev/null || echo "Process already stopped"
    rm -f .backend.pid
fi

# Kill any remaining uvicorn processes
pkill -f "uvicorn.*app.main:app" || echo "No uvicorn processes found"
```

#### 1.2 Verify Shutdown
```bash
# Wait for graceful shutdown
sleep 3

# Check if any processes remain
if pgrep -f "uvicorn.*app.main:app"; then
    echo "⚠️ Force killing remaining processes..."
    pkill -9 -f "uvicorn.*app.main:app"
fi

# Verify port is free
if lsof -i :8000; then
    echo "❌ Port 8000 still occupied"
    exit 1
else
    echo "✅ Port 8000 is free"
fi
```

### Step 2: Database Cleanup (Optional)

#### 2.1 Stop Database Services
```bash
# Only stop if you want to shut down databases too
read -p "Stop database services? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🗄️ Stopping database services..."
    docker-compose stop postgres mongodb
    echo "✅ Database services stopped"
else
    echo "ℹ️ Database services left running"
fi
```

### Step 3: Cleanup
```bash
echo "🧹 Cleaning up temporary files..."

# Remove temporary files
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
rm -f .backend.pid

echo "✅ Backend shutdown complete"
```

---

## Common Issues & Solutions

### Issue 1: Column ID Conflicts
**Error**: `Column object 'id' already assigned to Table`

**Solution**:
```bash
# Check BaseModel implementation
grep -n "sa_column=" app/models/base.py
# Should use sa_column_kwargs instead of sa_column=Column(...)
```

### Issue 2: Missing Dependencies
**Error**: `ModuleNotFoundError: No module named 'aiofiles'`

**Solution**:
```bash
pip install aiofiles==24.1.0 Pillow==10.1.0 python-magic==0.4.27
```

### Issue 3: Port Already in Use
**Error**: `[Errno 98] Address already in use`

**Solution**:
```bash
# Find process using port 8000
lsof -i :8000
# Kill the process
kill -9 <PID>
```

### Issue 4: Database Connection Failures
**Error**: Database connection timeout

**Solution**:
```bash
# Restart database services
docker-compose down
docker-compose up -d postgres mongodb
# Wait 30 seconds before starting backend
sleep 30
```

### Issue 5: Route Conflicts
**Error**: Duplicate route definitions

**Solution**:
```bash
# Check for duplicate @router.get() definitions
grep -rn "@.*_router.get" app/api/
# Ensure specific routes come before parameterized routes (/{id})
```

### Issue 6: FileMetadata Schema Issues
**Error**: `no such column: size_bytes`

**Solution**:
```bash
# Check FileMetadata model columns
grep -n "Field" app/models/file_new.py
# Ensure queries use correct column names (file_size, is_active)
```

---

## Monitoring & Logs

### Real-time Log Monitoring
```bash
# If backend is running in background
tail -f backend.log

# For systemwide logs
journalctl -f -u uvicorn
```

### Health Monitoring
```bash
# Quick health check
curl -s http://localhost:8000/health | python3 -m json.tool

# Continuous monitoring (run in separate terminal)
watch -n 5 'curl -s http://localhost:8000/health | jq .status'
```

### Performance Monitoring
```bash
# Check resource usage
htop | grep uvicorn

# Check database connections
netstat -an | grep :5432  # PostgreSQL
netstat -an | grep :27017 # MongoDB
```

---

## Automation Scripts

### Quick Start Script
Create `/scripts/start-backend.sh`:
```bash
#!/bin/bash
set -e
cd "$(dirname "$0")/.."

echo "🚀 Starting P2P Backend..."

# Run all startup checks
source docs/aadil_docs/backend-startup-shutdown-guide.md

echo "✅ Backend started successfully!"
```

### Quick Stop Script
Create `/scripts/stop-backend.sh`:
```bash
#!/bin/bash
cd "$(dirname "$0")/.."

echo "🛑 Stopping P2P Backend..."
pkill -f uvicorn || echo "No backend running"
echo "✅ Backend stopped"
```

---

## Emergency Procedures

### Complete Reset (Nuclear Option)
```bash
# Stop everything
pkill -f uvicorn
docker-compose down

# Clean Python cache
find . -name "*.pyc" -delete
find . -name "__pycache__" -exec rm -rf {} +

# Reset virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Restart databases
docker-compose up -d

# Wait and start backend
sleep 30
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Debug Mode Startup
```bash
# Start with maximum debugging
uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload \
    --log-level debug \
    --access-log \
    --use-colors
```

---

## Version History

- **v1.0** (2025-08-06): Initial comprehensive guide
- Created after resolving P3.5.FIX.01 backend startup issues
- Covers all major failure points and solutions
- Includes automation scripts and monitoring

---

**📝 Note**: Always follow these procedures in order. Each step builds on the previous one, and skipping steps can lead to the startup issues we're trying to avoid.

**⚠️ Important**: Keep this guide updated as the backend evolves. Add new common issues as they're discovered.
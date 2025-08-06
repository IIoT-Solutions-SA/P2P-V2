#!/bin/bash
# P2P Backend Quick Start Script
# Usage: ./scripts/start-backend.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Navigate to backend directory
cd "$(dirname "$0")/.."

echo -e "${BLUE}🚀 P2P Backend Quick Start${NC}"
echo "=================================="

# Step 1: Check for existing processes
echo -e "${YELLOW}📋 Step 1: Checking for existing backend...${NC}"
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend already running at http://localhost:8000${NC}"
    echo -e "${GREEN}📚 API docs: http://localhost:8000/docs${NC}"
    exit 0
fi

# Kill zombie processes
if pgrep -f uvicorn > /dev/null; then
    echo -e "${YELLOW}⚠️ Found zombie uvicorn processes - cleaning up...${NC}"
    pkill -f uvicorn || true
    sleep 2
fi

# Step 2: Environment setup
echo -e "${YELLOW}📋 Step 2: Setting up environment...${NC}"
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Virtual environment not found!${NC}"
    echo "Create it with: python3 -m venv venv"
    exit 1
fi

source venv/bin/activate
echo -e "${GREEN}✅ Virtual environment activated${NC}"

# Step 3: Check critical dependencies
echo -e "${YELLOW}📋 Step 3: Verifying dependencies...${NC}"
REQUIRED_PACKAGES=("fastapi" "sqlmodel" "asyncpg" "aiofiles" "Pillow" "python-magic")
MISSING_PACKAGES=()

for package in "${REQUIRED_PACKAGES[@]}"; do
    if ! pip show $package > /dev/null 2>&1; then
        MISSING_PACKAGES+=($package)
    fi
done

if [ ${#MISSING_PACKAGES[@]} -ne 0 ]; then
    echo -e "${YELLOW}⚠️ Installing missing packages: ${MISSING_PACKAGES[*]}${NC}"
    pip install aiofiles==24.1.0 Pillow==10.1.0 python-magic==0.4.27
fi
echo -e "${GREEN}✅ All dependencies verified${NC}"

# Step 4: Database services
echo -e "${YELLOW}📋 Step 4: Checking database services...${NC}"
if ! docker-compose ps | grep -q "postgres.*Up"; then
    echo -e "${YELLOW}⚠️ Starting PostgreSQL...${NC}"
    docker-compose up -d postgres
fi

if ! docker-compose ps | grep -q "mongodb.*Up"; then
    echo -e "${YELLOW}⚠️ Starting MongoDB...${NC}"
    docker-compose up -d mongodb
fi

echo -e "${YELLOW}⏳ Waiting for databases to be ready...${NC}"
sleep 10
echo -e "${GREEN}✅ Database services ready${NC}"

# Step 5: Model validation
echo -e "${YELLOW}📋 Step 5: Validating models...${NC}"
python3 -c "
try:
    from app.models.base import BaseModel
    from app.models.user import User
    from app.models.organization import Organization
    from app.models import FileMetadata
    print('✅ All models validated')
except Exception as e:
    print(f'❌ Model validation failed: {e}')
    exit(1)
" || (echo -e "${RED}❌ Model validation failed${NC}" && exit 1)

# Step 6: Start backend
echo -e "${YELLOW}📋 Step 6: Starting backend server...${NC}"
echo "Starting uvicorn on http://localhost:8000..."

# Start in background and capture PID
uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload \
    --timeout-keep-alive 30 \
    --log-level info &

BACKEND_PID=$!
echo $BACKEND_PID > .backend.pid

echo -e "${BLUE}Backend started with PID: $BACKEND_PID${NC}"

# Step 7: Verify startup
echo -e "${YELLOW}📋 Step 7: Verifying startup...${NC}"
echo -e "${YELLOW}⏳ Waiting for backend to start...${NC}"

MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s http://localhost:8000/health > /dev/null; then
        echo -e "${GREEN}✅ Backend health check passed${NC}"
        break
    else
        echo -n "."
        sleep 2
        ((RETRY_COUNT++))
    fi
done

echo ""

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo -e "${RED}❌ Backend failed to start within timeout${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

# Step 8: API verification
echo -e "${YELLOW}📋 Step 8: Testing core endpoints...${NC}"
ENDPOINTS=(
    "/health"
    "/api/v1/users/me"
    "/api/v1/organizations/me"
    "/api/v1/organizations/stats"
)

for endpoint in "${ENDPOINTS[@]}"; do
    response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000$endpoint)
    if [ "$response" = "200" ]; then
        echo -e "${GREEN}✅ $endpoint${NC}"
    else
        echo -e "${YELLOW}⚠️ $endpoint (HTTP $response)${NC}"
    fi
done

echo ""
echo -e "${GREEN}🎉 Backend startup complete!${NC}"
echo "=================================="
echo -e "${BLUE}📍 Backend URL:${NC} http://localhost:8000"
echo -e "${BLUE}📚 API Docs:${NC} http://localhost:8000/docs"
echo -e "${BLUE}📊 Interactive API:${NC} http://localhost:8000/redoc"
echo ""
echo -e "${YELLOW}💡 To stop the backend:${NC} ./scripts/stop-backend.sh"
echo -e "${YELLOW}📋 View logs:${NC} tail -f logs/backend.log"
echo ""
echo -e "${GREEN}Ready for development! 🚀${NC}"
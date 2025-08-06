#!/bin/bash
# P2P Backend Quick Stop Script
# Usage: ./scripts/stop-backend.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Navigate to backend directory
cd "$(dirname "$0")/.."

echo -e "${BLUE}🛑 P2P Backend Quick Stop${NC}"
echo "================================="

# Step 1: Stop backend process
echo -e "${YELLOW}📋 Step 1: Stopping backend process...${NC}"

# Check if backend is running
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️ No backend appears to be running${NC}"
else
    echo -e "${GREEN}✅ Backend detected, stopping...${NC}"
fi

# Stop using PID file if available
if [ -f ".backend.pid" ]; then
    BACKEND_PID=$(cat .backend.pid)
    echo -e "${BLUE}Found PID file: $BACKEND_PID${NC}"
    
    if kill -TERM $BACKEND_PID 2>/dev/null; then
        echo -e "${GREEN}✅ Sent SIGTERM to process $BACKEND_PID${NC}"
        sleep 3
        
        # Check if process still exists
        if kill -0 $BACKEND_PID 2>/dev/null; then
            echo -e "${YELLOW}⚠️ Process still running, force killing...${NC}"
            kill -9 $BACKEND_PID 2>/dev/null || true
        fi
    else
        echo -e "${YELLOW}⚠️ Process $BACKEND_PID not found (already stopped)${NC}"
    fi
    
    rm -f .backend.pid
    echo -e "${GREEN}✅ PID file removed${NC}"
fi

# Kill any remaining uvicorn processes
echo -e "${YELLOW}📋 Step 2: Cleaning up any remaining processes...${NC}"
UVICORN_PIDS=$(pgrep -f "uvicorn.*app.main:app" || echo "")

if [ -n "$UVICORN_PIDS" ]; then
    echo -e "${YELLOW}⚠️ Found additional uvicorn processes: $UVICORN_PIDS${NC}"
    pkill -f "uvicorn.*app.main:app" || true
    sleep 2
    
    # Force kill if still running
    if pgrep -f "uvicorn.*app.main:app" > /dev/null; then
        echo -e "${YELLOW}⚠️ Force killing stubborn processes...${NC}"
        pkill -9 -f "uvicorn.*app.main:app" || true
    fi
    echo -e "${GREEN}✅ All uvicorn processes stopped${NC}"
else
    echo -e "${GREEN}✅ No additional uvicorn processes found${NC}"
fi

# Step 3: Verify port is free
echo -e "${YELLOW}📋 Step 3: Verifying port 8000 is free...${NC}"
if lsof -i :8000 > /dev/null 2>&1; then
    echo -e "${RED}❌ Port 8000 still occupied:${NC}"
    lsof -i :8000
    echo -e "${YELLOW}You may need to manually kill the process${NC}"
else
    echo -e "${GREEN}✅ Port 8000 is free${NC}"
fi

# Step 4: Verify backend is stopped
echo -e "${YELLOW}📋 Step 4: Final verification...${NC}"
sleep 2

if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${RED}❌ Backend still responding - shutdown may have failed${NC}"
    echo -e "${YELLOW}Try running: pkill -9 -f uvicorn${NC}"
    exit 1
else
    echo -e "${GREEN}✅ Backend successfully stopped${NC}"
fi

# Step 5: Optional database shutdown
echo ""
read -p "$(echo -e ${YELLOW}Stop database services too? \(y/N\): ${NC})" -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}📋 Step 5: Stopping database services...${NC}"
    docker-compose stop postgres mongodb
    echo -e "${GREEN}✅ Database services stopped${NC}"
else
    echo -e "${BLUE}ℹ️ Database services left running${NC}"
fi

# Step 6: Cleanup
echo -e "${YELLOW}📋 Step 6: Cleaning up temporary files...${NC}"
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
rm -f .backend.pid

echo ""
echo -e "${GREEN}🎉 Backend shutdown complete!${NC}"
echo "================================="
echo -e "${BLUE}📍 Port 8000:${NC} Free"
echo -e "${BLUE}📋 Status:${NC} Stopped"
echo ""
echo -e "${YELLOW}💡 To start the backend again:${NC} ./scripts/start-backend.sh"
echo -e "${YELLOW}📚 Startup guide:${NC} docs/aadil_docs/backend-startup-shutdown-guide.md"
echo ""
echo -e "${GREEN}Safe to develop! ✅${NC}"
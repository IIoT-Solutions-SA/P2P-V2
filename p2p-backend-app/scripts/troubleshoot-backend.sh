#!/bin/bash
# P2P Backend Troubleshooting Script
# Usage: ./scripts/troubleshoot-backend.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Navigate to backend directory
cd "$(dirname "$0")/.."

echo -e "${BLUE}🔧 P2P Backend Troubleshooting${NC}"
echo "================================="

# System Information
echo -e "${YELLOW}📋 System Information${NC}"
echo "Working Directory: $(pwd)"
echo "Python Version: $(python3 --version)"
echo "User: $(whoami)"
echo ""

# Check 1: Process Status
echo -e "${YELLOW}📋 Check 1: Process Status${NC}"
echo "Current uvicorn processes:"
if pgrep -f uvicorn; then
    ps aux | grep uvicorn | grep -v grep
else
    echo -e "${GREEN}No uvicorn processes running${NC}"
fi
echo ""

# Check 2: Port Status
echo -e "${YELLOW}📋 Check 2: Port Status${NC}"
if lsof -i :8000; then
    echo -e "${RED}⚠️ Port 8000 is occupied${NC}"
else
    echo -e "${GREEN}✅ Port 8000 is free${NC}"
fi
echo ""

# Check 3: Backend Health
echo -e "${YELLOW}📋 Check 3: Backend Health${NC}"
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend is responding${NC}"
    curl -s http://localhost:8000/health | python3 -m json.tool 2>/dev/null || curl -s http://localhost:8000/health
else
    echo -e "${RED}❌ Backend not responding${NC}"
fi
echo ""

# Check 4: Virtual Environment
echo -e "${YELLOW}📋 Check 4: Virtual Environment${NC}"
if [ -d "venv" ]; then
    echo -e "${GREEN}✅ Virtual environment exists${NC}"
    echo "Python executable: $(which python3)"
    if [[ $(which python3) == *"venv"* ]]; then
        echo -e "${GREEN}✅ Virtual environment is activated${NC}"
    else
        echo -e "${YELLOW}⚠️ Virtual environment not activated${NC}"
        echo "Run: source venv/bin/activate"
    fi
else
    echo -e "${RED}❌ Virtual environment not found${NC}"
    echo "Create with: python3 -m venv venv"
fi
echo ""

# Check 5: Dependencies
echo -e "${YELLOW}📋 Check 5: Critical Dependencies${NC}"
REQUIRED_PACKAGES=("fastapi" "sqlmodel" "asyncpg" "aiofiles" "Pillow" "python-magic")
for package in "${REQUIRED_PACKAGES[@]}"; do
    if pip show $package > /dev/null 2>&1; then
        version=$(pip show $package | grep Version | cut -d' ' -f2)
        echo -e "${GREEN}✅ $package ($version)${NC}"
    else
        echo -e "${RED}❌ $package (missing)${NC}"
    fi
done
echo ""

# Check 6: Database Services
echo -e "${YELLOW}📋 Check 6: Database Services${NC}"
if docker-compose ps | grep -q "postgres.*Up"; then
    echo -e "${GREEN}✅ PostgreSQL running${NC}"
else
    echo -e "${RED}❌ PostgreSQL not running${NC}"
fi

if docker-compose ps | grep -q "mongodb.*Up"; then
    echo -e "${GREEN}✅ MongoDB running${NC}"
else
    echo -e "${RED}❌ MongoDB not running${NC}"
fi
echo ""

# Check 7: Model Import Test
echo -e "${YELLOW}📋 Check 7: Model Import Test${NC}"
python3 -c "
try:
    from app.models.base import BaseModel
    from app.models.user import User  
    from app.models.organization import Organization
    from app.models import FileMetadata
    print('✅ All models import successfully')
except Exception as e:
    print(f'❌ Model import failed: {e}')
    import traceback
    traceback.print_exc()
" 2>&1 || echo -e "${RED}❌ Model import test failed${NC}"
echo ""

# Check 8: File System
echo -e "${YELLOW}📋 Check 8: File System${NC}"
CRITICAL_FILES=(
    "app/main.py"
    "app/models/base.py"
    "app/api/v1/api.py"
    "requirements.txt"
    ".env"
    "docker-compose.yml"
)

for file in "${CRITICAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅ $file${NC}"
    else
        echo -e "${RED}❌ $file (missing)${NC}"
    fi
done
echo ""

# Check 9: Logs Analysis
echo -e "${YELLOW}📋 Check 9: Recent Log Errors${NC}"
if [ -f "backend.log" ]; then
    echo "Last 10 error lines from backend.log:"
    tail -100 backend.log | grep -i error | tail -10 || echo "No recent errors found"
else
    echo -e "${YELLOW}⚠️ No backend.log file found${NC}"
fi
echo ""

# Common Issues & Solutions
echo -e "${BLUE}🔧 Common Issues & Quick Fixes${NC}"
echo "================================="

echo -e "${YELLOW}Issue: Port 8000 occupied${NC}"
echo "Solution: pkill -f uvicorn"
echo ""

echo -e "${YELLOW}Issue: Column ID conflicts${NC}" 
echo "Solution: Check app/models/base.py uses sa_column_kwargs"
echo ""

echo -e "${YELLOW}Issue: Missing dependencies${NC}"
echo "Solution: pip install aiofiles==24.1.0 Pillow==10.1.0 python-magic==0.4.27"
echo ""

echo -e "${YELLOW}Issue: Database not running${NC}"
echo "Solution: docker-compose up -d postgres mongodb"
echo ""

echo -e "${YELLOW}Issue: Route conflicts${NC}"
echo "Solution: Check /organization comes before /{user_id} in routes"
echo ""

# Emergency Reset
echo -e "${BLUE}🚨 Emergency Reset Commands${NC}"
echo "================================="
echo "Complete reset:"
echo "  pkill -f uvicorn"
echo "  docker-compose down"
echo "  docker-compose up -d"
echo "  sleep 30"
echo "  ./scripts/start-backend.sh"
echo ""

echo -e "${GREEN}Troubleshooting complete! 🔧${NC}"
echo ""
echo -e "${YELLOW}💡 Need more help? Check:${NC}"
echo "📚 docs/aadil_docs/backend-startup-shutdown-guide.md"
echo "🚀 Use: ./scripts/start-backend.sh for guided startup"
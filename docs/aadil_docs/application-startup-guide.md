# Application Startup Guide

## 🚀 Quick Start (Recommended)

### Complete Application Startup & Shutdown

```bash
# ✅ GRACEFUL STARTUP
# 1. Backend (from backend directory)
cd /mnt/d/Projects/P2P-V2/p2p-backend-app
docker-compose up -d

# 2. Frontend (from frontend directory) 
cd /mnt/d/Projects/P2P-V2/p2p-frontend-app
./frontend-control.sh start

# ✅ GRACEFUL SHUTDOWN
# 1. Frontend
cd /mnt/d/Projects/P2P-V2/p2p-frontend-app
./frontend-control.sh stop

# 2. Backend (from backend directory)
cd /mnt/d/Projects/P2P-V2/p2p-backend-app
docker-compose down
```

### Access Points
- 🖥️ **Frontend**: http://localhost:5173
- 🔧 **Backend API**: http://localhost:8000  
- 📊 **API Documentation**: http://localhost:8000/docs

## Backend Management

### ⚠️ Directory Requirement
**ALL backend commands MUST be run from:** `/mnt/d/Projects/P2P-V2/p2p-backend-app`

### Commands
```bash
# Start
docker-compose up -d

# Stop  
docker-compose down

# Restart specific service
docker-compose restart backend

# View logs
docker-compose logs -f backend

# Health check
curl http://localhost:8000/health
```

## Frontend Management

### ⚠️ Directory Requirement  
**ALL frontend commands MUST be run from:** `/mnt/d/Projects/P2P-V2/p2p-frontend-app`

### Using Frontend Control Script (Recommended)
```bash
# Start (graceful with readiness detection)
./frontend-control.sh start

# Stop (graceful by port)
./frontend-control.sh stop

# Restart
./frontend-control.sh restart

# Status check
./frontend-control.sh status

# View logs
tail -f frontend.log
```

### Manual Method (Alternative)
```bash
# Start manually
nohup npm run dev > frontend.log 2>&1 &

# Stop manually 
pkill -f "vite"
```

## Development Workflow

### Daily Startup
```bash
# Quick start everything
cd /mnt/d/Projects/P2P-V2/p2p-backend-app && docker-compose up -d && \
cd /mnt/d/Projects/P2P-V2/p2p-frontend-app && ./frontend-control.sh start
```

### Daily Shutdown
```bash
# Quick stop everything  
cd /mnt/d/Projects/P2P-V2/p2p-frontend-app && ./frontend-control.sh stop && \
cd /mnt/d/Projects/P2P-V2/p2p-backend-app && docker-compose down
```

### After Code Changes

**Backend Python Code**: Auto-reloads, no action needed  
**Frontend Code**: Hot-reloads automatically, no action needed

**Backend Dependencies** (requirements.txt):
```bash
cd /mnt/d/Projects/P2P-V2/p2p-backend-app
docker-compose build backend
docker-compose up -d backend
```

**Frontend Dependencies** (package.json):
```bash
cd /mnt/d/Projects/P2P-V2/p2p-frontend-app
./frontend-control.sh stop
npm install  
./frontend-control.sh start
```

## Status Check

### Quick Status
```bash
# Backend
curl -s http://localhost:8000/health | python3 -c "import sys,json; print('Backend:', json.load(sys.stdin)['status'])"

# Frontend
cd /mnt/d/Projects/P2P-V2/p2p-frontend-app && ./frontend-control.sh status
```

### Detailed Status
```bash
cd /mnt/d/Projects/P2P-V2/p2p-backend-app && docker-compose ps && \
echo "" && curl -s http://localhost:8000/health | python3 -m json.tool
```

## Troubleshooting

### Port Issues
```bash
# Check what's using ports
lsof -i :8000  # Backend
lsof -i :5173  # Frontend

# Kill process using port
kill -9 <PID>
```

### Service Issues  
```bash
# Backend logs
cd /mnt/d/Projects/P2P-V2/p2p-backend-app
docker-compose logs backend

# Frontend logs
cd /mnt/d/Projects/P2P-V2/p2p-frontend-app
tail -50 frontend.log
```

### Complete Reset
```bash
# Stop everything
cd /mnt/d/Projects/P2P-V2/p2p-frontend-app && ./frontend-control.sh stop
cd /mnt/d/Projects/P2P-V2/p2p-backend-app && docker-compose down

# Remove all data (WARNING: deletes all data)
cd /mnt/d/Projects/P2P-V2/p2p-backend-app && docker-compose down -v

# Fresh start
cd /mnt/d/Projects/P2P-V2/p2p-backend-app && docker-compose up -d
cd /mnt/d/Projects/P2P-V2/p2p-frontend-app && ./frontend-control.sh start
```

## Service Architecture

### Backend Services (Docker)
- **PostgreSQL** (port 5432) - Main database
- **MongoDB** (port 27017) - Document store  
- **Redis** (port 6379) - Cache
- **SuperTokens** (port 3567) - Authentication
- **Backend API** (port 8000) - FastAPI application

### Frontend Service
- **Vite Dev Server** (port 5173) - React application
- **Startup Time**: ~3 seconds consistently
- **Process Management**: Port-based identification (reliable)

## Important Notes

1. **Frontend Control Script**: Use `./frontend-control.sh` for reliable process management
2. **Graceful Operations**: Always use proper startup/shutdown methods  
3. **Directory Requirements**: Commands must be run from correct directories
4. **Auto-reload**: Both backend and frontend support hot-reloading during development
5. **Logs**: Frontend logs saved to `frontend.log`, backend via `docker-compose logs`

## Quick Reference

```bash
# Status check
curl http://localhost:8000/health && ./frontend-control.sh status

# Full restart
./frontend-control.sh stop && docker-compose down && \
docker-compose up -d && ./frontend-control.sh start

# View all logs
docker-compose logs -f backend &  # Backend  
tail -f frontend.log              # Frontend
```
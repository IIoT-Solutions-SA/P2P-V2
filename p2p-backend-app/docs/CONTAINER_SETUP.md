# Container Setup Guide

## Overview
This guide helps you get the P2P Sandbox backend running with Docker containers.

## Prerequisites
- Docker Desktop installed and running
- At least 4GB of free RAM
- Port availability: 8000, 5432, 27017, 6379, 3567

## Quick Start

1. **Clone and navigate to backend**
   ```bash
   cd p2p-backend-app
   ```

2. **Set up environment**
   ```bash
   cp .env.example .env
   # Edit .env if needed (usually defaults work fine)
   ```

3. **Start all services**
   ```bash
   docker-compose up -d
   ```

4. **Check health**
   ```bash
   ./scripts/check-health.sh
   ```

## Services Overview

| Service | Port | Purpose |
|---------|------|---------|
| Backend | 8000 | FastAPI application |
| PostgreSQL | 5432 | Main database |
| MongoDB | 27017 | Document storage |
| Redis | 6379 | Caching & sessions |
| SuperTokens | 3567 | Authentication |

## Common Commands

### Start Services
```bash
# Start all services in background
docker-compose up -d

# Start and watch logs
docker-compose up

# Start specific service
docker-compose up postgres
```

### Stop Services
```bash
# Stop all services
docker-compose down

# Stop and remove volumes (CAUTION: deletes data)
docker-compose down -v
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
```

### Access Containers
```bash
# PostgreSQL
docker-compose exec postgres psql -U postgres -d p2p_sandbox

# MongoDB
docker-compose exec mongodb mongosh p2p_sandbox

# Redis
docker-compose exec redis redis-cli

# Backend shell
docker-compose exec backend bash
```

## Troubleshooting

### Port Already in Use
```bash
# Find what's using a port (e.g., 8000)
lsof -i :8000  # Mac/Linux
netstat -ano | findstr :8000  # Windows

# Change port in docker-compose.yml if needed
```

### Container Won't Start
```bash
# Check logs
docker-compose logs [service_name]

# Rebuild image
docker-compose build --no-cache [service_name]
```

### Database Connection Issues
```bash
# Ensure database is ready
docker-compose ps  # Should show "healthy"

# Test connection
docker-compose exec backend python -c "print('Testing connection...')"
```

### Reset Everything
```bash
# Stop and remove everything
docker-compose down -v

# Remove all Docker data (CAUTION!)
docker system prune -a
```

## Development Tips

1. **Hot Reload**: Backend automatically reloads on code changes
2. **Debugging**: Port 5678 is exposed for Python debugger
3. **Database GUI**: Use tools like pgAdmin or MongoDB Compass
4. **API Docs**: Visit http://localhost:8000/docs once backend is running

## Next Steps
Once containers are running:
1. Create FastAPI application structure
2. Set up database models
3. Implement authentication
4. Start building features!

## Health Check Results

When all services are healthy, you should see:
```
✓ PostgreSQL is healthy
✓ MongoDB is healthy
✓ Redis is healthy
✓ SuperTokens is healthy
```
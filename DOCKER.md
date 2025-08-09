# Docker Setup for P2P Sandbox

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
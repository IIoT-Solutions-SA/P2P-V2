# Docker Infrastructure Exploration Log

**Date:** 2026-03-05
**Session:** 006
**Agent:** Docker Explorer

## Objective

Comprehensive exploration of the `docker/` directory — all Docker Compose files, Dockerfiles, init scripts, nginx config, and infrastructure wiring.

## Summary

The P2P platform uses 5 containerized services orchestrated via Docker Compose with separate development and production configurations. Infrastructure includes PostgreSQL, MongoDB, SuperTokens, a FastAPI backend, and a React frontend, all connected on a custom bridge network with health checks, volume persistence, and log rotation.

---

## Directory Structure

```
docker/
├── docker-compose.yml              # Production compose configuration
├── development_docker-compose.yml   # Development compose configuration
├── backend.Dockerfile               # Backend Python service build (multi-stage)
├── frontend.Dockerfile              # Frontend React service build (multi-stage)
├── init-db.sql                      # PostgreSQL initialization script
└── nginx.conf                       # Nginx reverse proxy configuration (production)
```

---

## Complete Service Topology

### 1. PostgreSQL Database (`postgres:16-alpine`)
- **Container name**: `p2p-postgres`
- **Port**: `5432:5432`
- **Credentials**: `p2p_user` / `iiot123`
- **Databases**:
  - `p2p_sandbox` (main app data — created via POSTGRES_DB env var)
  - `supertokens` (auth data — created by `init-db.sql`)
- **Volumes**:
  - `postgres_data:/var/lib/postgresql/data` (persistent data)
  - `./init-db.sql:/docker-entrypoint-initdb.d/init.sql` (first-boot init)
- **Healthcheck**: `pg_isready -U p2p_user -d p2p_sandbox` (interval: 5s, timeout: 5s, retries: 5)
- **Logging**: JSON driver, 10MB max, 3 files rotation

### 2. MongoDB Database (`mongo:7`)
- **Container name**: `p2p-mongodb`
- **Port**: `27017:27017`
- **Credentials**: Root user `p2p_user` / `iiot123`, authSource: `admin`
- **Database**: `p2p_sandbox`
- **Volumes**: `mongodb_data:/data/db` (persistent data)
- **Healthcheck**: `mongosh --eval "db.adminCommand('ping')"` (interval: 5s, timeout: 5s, retries: 5)
- **Logging**: JSON driver, 10MB max, 3 files rotation

### 3. SuperTokens Authentication (`supertokens-postgresql:11.0`)
- **Container name**: `p2p-supertokens`
- **Port**: `3567:3567`
- **Database**: Connects to PostgreSQL `supertokens` database
- **Connection URI**: `postgresql://p2p_user:iiot123@postgres:5432/supertokens`
- **Dependencies**: Requires PostgreSQL to be healthy
- **Logging**: JSON driver, 10MB max, 3 files rotation

### 4. Backend Service (FastAPI Python)
- **Container name**: `p2p-backend`
- **Port**: `8000:8000`
- **User**: Non-root `appuser:appuser` (UID 1000:1000)
- **Healthcheck**: `curl -f http://localhost:8000/api/v1/health` (interval: 10s, timeout: 10s, retries: 5, start period: 15s)
- **Dependencies**: PostgreSQL (healthy), MongoDB (healthy), SuperTokens (started)
- **Volume**: `../p2p-backend-app:/app` (entire backend codebase mounted)
- **Startup sequence**:
  1. Waits for PostgreSQL on port 5432 (socket connection check loop)
  2. Waits for MongoDB on port 27017 (socket connection check loop)
  3. Runs `alembic upgrade head` (database migrations)
  4. Starts uvicorn server

### 5. Frontend Service (React + Vite)
- **Container name**: `p2p-frontend`
- **Dependencies**: Backend must be healthy
- **Logging**: JSON driver, 10MB max, 3 files rotation

---

## Dockerfile Details

### `backend.Dockerfile` (Multi-Stage Build)
- **Base image**: `python:3.11-slim`
- **Security**: Runs as non-root user `appuser` (UID 1000:1000)
- **Workdir**: `/app`
- **Environment**: `PYTHONUNBUFFERED=1`, `PYTHONDONTWRITEBYTECODE=1`, `PIP_NO_CACHE_DIR=1`
- **Development stage**: Installs `gcc` + `curl`, runs with `--reload` (hot reload)
- **Production stage**: Installs only `curl`, runs with `--workers 4`

### `frontend.Dockerfile` (Multi-Stage Build)
- **Base image (dev)**: `node:20-alpine`
- **Base image (prod)**: `nginx:1.25-alpine`
- **Development stage**: Runs Vite dev server on port 5173 with `npm run dev -- --host`
- **Build stage**: Runs `npm ci` + `npm run build` → produces `dist/` folder
- **Production stage**: Copies `dist/` to nginx HTML root, uses custom `nginx.conf`

---

## Nginx Configuration (`nginx.conf`)

```nginx
server {
  listen 80;
  server_name localhost;
  root /usr/share/nginx/html;
  index index.html;

  location / {
    try_files $uri /index.html;
  }
}
```

**Purpose**: SPA routing — all non-file requests redirect to `index.html` for React Router to handle client-side routing on page reload.

---

## Init Script (`init-db.sql`)

```sql
CREATE DATABASE supertokens;
```

Runs on first PostgreSQL container startup only. Creates a separate database for the SuperTokens auth service, keeping auth data isolated from app data.

---

## Development vs Production Differences

| Aspect | Development | Production |
|--------|-------------|-----------|
| **Docker Target** | `development` | `production` |
| **Backend Workers** | 1 (with `--reload`) | 4 (production workers) |
| **Frontend Serving** | Vite dev server (port 5173) | Nginx static files (port 80) |
| **Frontend Port Map** | `5173:5173` | `5173:80` |
| **CORS Origins** | `["http://localhost:5173"]` | `["http://15.185.167.236:5173"]` |
| **API Domain** | `http://localhost:8000` | `http://15.185.167.236:8000` |
| **Website Domain** | `http://localhost:5173` | `http://15.185.167.236:5173` |
| **Frontend Volumes** | Mounted (hot reload enabled) | None (static built artifacts) |
| **Frontend node_modules** | Anonymous volume (preserved) | N/A |
| **Frontend Mode** | `MODE=development` env var | N/A |
| **Debug** | `true` | `true` (should be `false`) |
| **Log Level** | `DEBUG` | `DEBUG` (should be `INFO`) |

---

## Persistent Volumes

1. **`postgres_data`** — PostgreSQL data at `/var/lib/postgresql/data`
   - Stores: User core records, SuperTokens session data
2. **`mongodb_data`** — MongoDB data at `/data/db`
   - Stores: Extended profiles, organizations, use cases, forums, invitations

---

## Network Architecture

- **Network name**: `p2p-network` (bridge driver)
- All 5 services on the same custom bridge network
- Internal service-to-service communication via container names:
  - Backend → `postgres:5432`
  - Backend → `mongodb:27017`
  - Backend → `supertokens:3567`
- Frontend → Backend communication via environment-configured URLs (external)

---

## Startup Sequence (Orchestrated)

1. **PostgreSQL starts** → runs `init-db.sql` → creates `supertokens` DB
2. **PostgreSQL healthcheck passes** → `pg_isready` succeeds
3. **MongoDB starts** → initializes with root credentials
4. **MongoDB healthcheck passes** → `mongosh ping` succeeds
5. **SuperTokens starts** → connects to PostgreSQL `supertokens` database
6. **Backend starts** (after PG + Mongo healthy):
   - Socket-checks PostgreSQL connectivity (loop until connected)
   - Socket-checks MongoDB connectivity (loop until connected)
   - Runs `alembic upgrade head` (applies pending migrations)
   - Starts FastAPI server with uvicorn
7. **Backend healthcheck passes** → `/api/v1/health` returns 200
8. **Frontend starts** (after backend healthy):
   - Dev: Vite dev server with hot reload
   - Prod: Nginx serves static React build

---

## Backend Environment Variables (Full List)

```env
DATABASE_URL=postgresql+asyncpg://p2p_user:iiot123@postgres:5432/p2p_sandbox
MONGODB_URL=mongodb://p2p_user:iiot123@mongodb:27017/p2p_sandbox?authSource=admin
SUPERTOKENS_CONNECTION_URI=http://supertokens:3567
BACKEND_CORS_ORIGINS=["http://localhost:5173"]          # dev
BACKEND_CORS_ORIGINS=["http://15.185.167.236:5173"]     # prod
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=true
LOG_LEVEL=DEBUG
API_DOMAIN=http://localhost:8000                         # dev
API_DOMAIN=http://15.185.167.236:8000                    # prod
WEBSITE_DOMAIN=http://localhost:5173                      # dev
WEBSITE_DOMAIN=http://15.185.167.236:5173                # prod
```

---

## Key Implementation Details

1. **Socket connection checks**: Backend uses custom Python socket loops (not just Docker `depends_on`) to ensure true database connectivity before running Alembic migrations
2. **Multi-stage frontend build**: Production image is ~8-10MB (nginx + built assets) vs ~500MB+ development image with node_modules
3. **Non-root execution**: Backend runs as `appuser` (UID 1000) for container security
4. **Log rotation**: All services use JSON logging with 10MB max file size and 3 files retained
5. **SuperTokens isolation**: Separate PostgreSQL database (`supertokens`) from app data (`p2p_sandbox`)
6. **SPA routing**: Nginx `try_files` ensures React Router handles all client-side routes on page refresh

---

## File Paths Inside Containers

**Backend container**:
- Source code: `/app/`
- Migrations: `/app/alembic/versions/`
- Logs: `/app/logs/`
- Main app entry: `/app/app/main.py`

**Frontend container (dev)**:
- Source code: `/app/`
- Node modules: `/app/node_modules` (anonymous volume)

**Frontend container (prod)**:
- Built app: `/usr/share/nginx/html/`
- Nginx config: `/etc/nginx/conf.d/default.conf`

---

## Notes

- Production compose still has `DEBUG=true` and `LOG_LEVEL=DEBUG` — should be changed for real production
- `SECRET_KEY` placeholder should be replaced with a strong random key in production
- Database credentials are hardcoded in compose files — consider using Docker secrets or `.env` files for production
- The `15.185.167.236` IP appears to be an AWS/cloud server IP used for production deployment

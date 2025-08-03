# Story 6: Docker Containerization

## Story Details
**Epic**: Epic 1 - Project Foundation & Development Environment  
**Story Points**: 6  
**Priority**: High  
**Dependencies**: All previous stories (1-5)

## User Story
**As a** developer  
**I want** all services containerized with Docker  
**So that** I can run the entire stack consistently with one command

## Acceptance Criteria
- [ ] Dockerfile for frontend application with multi-stage build
- [ ] Dockerfile for backend application with optimized Python image
- [ ] docker-compose.yml orchestrating all services
- [ ] Volume mounts for development hot-reloading
- [ ] Network configuration for inter-service communication
- [ ] Container health checks implemented for all services
- [ ] Development and production configurations separated
- [ ] Environment variable management across containers
- [ ] Container logs aggregated and accessible

## Technical Specifications

### 1. Frontend Dockerfile

#### frontend/Dockerfile
```dockerfile
# Multi-stage build for React + Vite
FROM node:18-alpine AS development

WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Expose development port
EXPOSE 3000

# Development command with hot reload
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# Production build stage
FROM node:18-alpine AS build

WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine AS production

# Copy built application
COPY --from=build /app/dist /usr/share/nginx/html

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost/health || exit 1

CMD ["nginx", "-g", "daemon off;"]
```

#### frontend/nginx.conf
```nginx
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml text/javascript;
    
    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    server {
        listen 80;
        server_name localhost;
        root /usr/share/nginx/html;
        index index.html;
        
        # Handle React Router
        location / {
            try_files $uri $uri/ /index.html;
        }
        
        # Health check endpoint
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
        
        # API proxy (for development)
        location /api/ {
            proxy_pass http://backend:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # Auth proxy
        location /auth/ {
            proxy_pass http://backend:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

#### frontend/.dockerignore
```
node_modules
npm-debug.log
.git
.gitignore
README.md
.env
.env.local
.env.development.local
.env.test.local
.env.production.local
dist
build
coverage
.nyc_output
```

### 2. Backend Dockerfile

#### backend/Dockerfile
```dockerfile
FROM python:3.11-slim AS base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN groupadd -r appuser && useradd --no-log-init -r -g appuser appuser

WORKDIR /app

# Development stage
FROM base AS development

# Copy requirements first for better caching
COPY requirements.txt requirements-dev.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-dev.txt

# Copy source code
COPY . .

# Create logs directory
RUN mkdir -p logs && chown appuser:appuser logs

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/api/v1/health/ || exit 1

# Development command with auto-reload
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Production stage
FROM base AS production

# Copy requirements
COPY requirements.txt ./

# Install only production dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Create logs directory
RUN mkdir -p logs && chown appuser:appuser logs

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/api/v1/health/ || exit 1

# Production command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

#### backend/.dockerignore
```
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env
pip-log.txt
.tox
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git
.mypy_cache
.ruff_cache
.pytest_cache
.hypothesis
.venv
venv/
.env
.env.local
.DS_Store
```

### 3. Docker Compose Configuration

#### docker-compose.yml
```yaml
version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:16-alpine
    container_name: p2p-postgres
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-p2p_sandbox}
      POSTGRES_USER: ${POSTGRES_USER:-p2p_user}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-changeme}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./infrastructure/postgres/init.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - p2p-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-p2p_user} -d ${POSTGRES_DB:-p2p_sandbox}"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 30s

  # MongoDB
  mongodb:
    image: mongo:7
    container_name: p2p-mongodb
    environment:
      MONGO_INITDB_ROOT_USERNAME: ${MONGODB_USERNAME:-p2p_user}
      MONGO_INITDB_ROOT_PASSWORD: ${MONGODB_PASSWORD:-changeme}
      MONGO_INITDB_DATABASE: ${MONGODB_DATABASE:-p2p_sandbox}
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db
      - ./infrastructure/mongodb/init.js:/docker-entrypoint-initdb.d/init.js
    networks:
      - p2p-network
    healthcheck:
      test: ["CMD", "mongosh", "--eval", "db.adminCommand('ping')"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 30s

  # SuperTokens
  supertokens:
    image: registry.supertokens.io/supertokens/supertokens-postgresql:7.0
    container_name: p2p-supertokens
    environment:
      POSTGRESQL_CONNECTION_URI: postgresql://${POSTGRES_USER:-p2p_user}:${POSTGRES_PASSWORD:-changeme}@postgres:5432/supertokens
    ports:
      - "3567:3567"
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - p2p-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3567/hello"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 30s

  # Backend API
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
      target: development
    container_name: p2p-backend
    environment:
      - DATABASE_URL=postgresql+asyncpg://${POSTGRES_USER:-p2p_user}:${POSTGRES_PASSWORD:-changeme}@postgres:5432/${POSTGRES_DB:-p2p_sandbox}
      - MONGODB_URL=mongodb://${MONGODB_USERNAME:-p2p_user}:${MONGODB_PASSWORD:-changeme}@mongodb:27017/${MONGODB_DATABASE:-p2p_sandbox}?authSource=admin
      - SUPERTOKENS_CONNECTION_URI=http://supertokens:3567
      - BACKEND_CORS_ORIGINS=["http://localhost:3000","http://frontend:80"]
      - DEBUG=true
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
      - backend_logs:/app/logs
    depends_on:
      postgres:
        condition: service_healthy
      mongodb:
        condition: service_healthy
      supertokens:
        condition: service_healthy
    networks:
      - p2p-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health/"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 60s

  # Frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      target: development
    container_name: p2p-frontend
    environment:
      - VITE_API_URL=http://localhost:8000
      - VITE_SUPERTOKENS_API_DOMAIN=http://localhost:8000
      - VITE_SUPERTOKENS_WEBSITE_DOMAIN=http://localhost:3000
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    depends_on:
      backend:
        condition: service_healthy
    networks:
      - p2p-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 30s

volumes:
  postgres_data:
    driver: local
  mongodb_data:
    driver: local
  backend_logs:
    driver: local

networks:
  p2p-network:
    driver: bridge
```

#### docker-compose.prod.yml
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - p2p-network
    restart: unless-stopped

  mongodb:
    image: mongo:7
    environment:
      MONGO_INITDB_ROOT_USERNAME: ${MONGODB_USERNAME}
      MONGO_INITDB_ROOT_PASSWORD: ${MONGODB_PASSWORD}
      MONGO_INITDB_DATABASE: ${MONGODB_DATABASE}
    volumes:
      - mongodb_data:/data/db
    networks:
      - p2p-network
    restart: unless-stopped

  supertokens:
    image: registry.supertokens.io/supertokens/supertokens-postgresql:7.0
    environment:
      POSTGRESQL_CONNECTION_URI: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/supertokens
    depends_on:
      - postgres
    networks:
      - p2p-network
    restart: unless-stopped

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
      target: production
    environment:
      - DATABASE_URL=postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      - MONGODB_URL=mongodb://${MONGODB_USERNAME}:${MONGODB_PASSWORD}@mongodb:27017/${MONGODB_DATABASE}?authSource=admin
      - SUPERTOKENS_CONNECTION_URI=http://supertokens:3567
      - BACKEND_CORS_ORIGINS=${BACKEND_CORS_ORIGINS}
      - DEBUG=false
    volumes:
      - backend_logs:/app/logs
    depends_on:
      - postgres
      - mongodb
      - supertokens
    networks:
      - p2p-network
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      target: production
    environment:
      - VITE_API_URL=${FRONTEND_API_URL}
      - VITE_SUPERTOKENS_API_DOMAIN=${SUPERTOKENS_API_DOMAIN}
      - VITE_SUPERTOKENS_WEBSITE_DOMAIN=${SUPERTOKENS_WEBSITE_DOMAIN}
    depends_on:
      - backend
    networks:
      - p2p-network
    restart: unless-stopped

  # Reverse proxy for production
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./infrastructure/nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./infrastructure/nginx/ssl:/etc/nginx/ssl
    depends_on:
      - frontend
      - backend
    networks:
      - p2p-network
    restart: unless-stopped

volumes:
  postgres_data:
  mongodb_data:
  backend_logs:

networks:
  p2p-network:
    driver: bridge
```

### 4. Database Initialization Scripts

#### infrastructure/postgres/init.sql
```sql
-- Create additional databases
CREATE DATABASE supertokens;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE p2p_sandbox TO p2p_user;
GRANT ALL PRIVILEGES ON DATABASE supertokens TO p2p_user;

-- Create extensions if needed
\c p2p_sandbox;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
```

#### infrastructure/mongodb/init.js
```javascript
// Initialize MongoDB collections and indexes
db = db.getSiblingDB('p2p_sandbox');

// Create collections
db.createCollection('users');
db.createCollection('forum_posts');
db.createCollection('forum_replies');
db.createCollection('use_cases');

// Create indexes
db.users.createIndex({ "email": 1 }, { unique: true });
db.users.createIndex({ "expertise_tags": 1 });

db.forum_posts.createIndex({ "category": 1 });
db.forum_posts.createIndex({ "tags": 1 });
db.forum_posts.createIndex({ "created_at": -1 });

db.forum_replies.createIndex({ "post_id": 1 });
db.forum_replies.createIndex({ "created_at": 1 });

db.use_cases.createIndex({ "industry_tags": 1 });
db.use_cases.createIndex({ "region": 1 });
db.use_cases.createIndex({ "location": "2d" });

print('MongoDB initialization complete');
```

### 5. Development Scripts

#### scripts/dev-setup.sh
```bash
#!/bin/bash

# Development environment setup script

set -e

echo "🚀 Setting up P2P Sandbox development environment..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop."
    exit 1
fi

# Copy environment files if they don't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
fi

if [ ! -f frontend/.env ]; then
    echo "📝 Creating frontend/.env file..."
    cp frontend/.env.example frontend/.env
fi

if [ ! -f backend/.env ]; then
    echo "📝 Creating backend/.env file..."
    cp backend/.env.example backend/.env
fi

# Build and start all services
echo "🏗️  Building and starting services..."
docker-compose down -v  # Clean start
docker-compose build
docker-compose up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
timeout 300 bash -c 'until docker-compose ps | grep -q "healthy"; do sleep 5; done'

# Run database migrations
echo "🗄️  Running database migrations..."
docker-compose exec backend alembic upgrade head

# Seed development data
echo "🌱 Seeding development data..."
docker-compose exec backend python scripts/seed_db.py

echo "✅ Development environment is ready!"
echo ""
echo "🌐 Frontend: http://localhost:3000"
echo "🚀 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo "🔐 SuperTokens: http://localhost:3567"
echo ""
echo "📊 View logs: docker-compose logs -f"
echo "🛑 Stop services: docker-compose down"
```

#### scripts/prod-deploy.sh
```bash
#!/bin/bash

# Production deployment script

set -e

echo "🚀 Deploying P2P Sandbox to production..."

# Validate environment variables
required_vars=("POSTGRES_PASSWORD" "MONGODB_PASSWORD" "SUPERTOKENS_API_KEY")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Required environment variable $var is not set"
        exit 1
    fi
done

# Pull latest code
git pull origin main

# Build production images
echo "🏗️  Building production images..."
docker-compose -f docker-compose.prod.yml build

# Deploy with zero downtime
echo "🚀 Deploying services..."
docker-compose -f docker-compose.prod.yml up -d

# Run health checks
echo "🩺 Running health checks..."
sleep 30
docker-compose -f docker-compose.prod.yml ps

echo "✅ Production deployment complete!"
```

### 6. Docker Health Checks

Update backend health endpoint in app/api/v1/endpoints/health.py:
```python
@router.get("/docker")
async def docker_health():
    """Docker container health check"""
    return {"status": "healthy", "container": "backend"}
```

### 7. Monitoring and Logging

#### docker-compose.monitoring.yml
```yaml
version: '3.8'

services:
  # Application services from main docker-compose.yml
  
  # Prometheus for metrics
  prometheus:
    image: prom/prometheus:latest
    container_name: p2p-prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./infrastructure/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
    networks:
      - p2p-network

  # Grafana for dashboards
  grafana:
    image: grafana/grafana:latest
    container_name: p2p-grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
    networks:
      - p2p-network

volumes:
  grafana_data:

networks:
  p2p-network:
    external: true
```

## Implementation Steps

1. **Create Docker Files**
   ```bash
   # Create all Dockerfile and configuration files
   mkdir -p infrastructure/{docker,nginx,prometheus,postgres,mongodb}
   ```

2. **Build Development Environment**
   ```bash
   chmod +x scripts/dev-setup.sh
   ./scripts/dev-setup.sh
   ```

3. **Test All Services**
   ```bash
   # Check service health
   docker-compose ps
   
   # View logs
   docker-compose logs -f
   
   # Test endpoints
   curl http://localhost:8000/api/v1/health/
   curl http://localhost:3000/health
   ```

4. **Verify Hot Reloading**
   - Make changes to frontend and backend code
   - Verify changes reflect without rebuilding

## Testing Checklist
- [ ] All services start successfully
- [ ] Health checks pass for all containers
- [ ] Frontend accessible at http://localhost:3000
- [ ] Backend API accessible at http://localhost:8000
- [ ] Database connections working
- [ ] SuperTokens accessible at http://localhost:3567
- [ ] Hot reloading works for development
- [ ] Production build creates optimized images
- [ ] Container logs are accessible

## Production Considerations
- [ ] Use secrets management for sensitive data
- [ ] Configure SSL/TLS termination
- [ ] Set up reverse proxy with nginx
- [ ] Implement container orchestration (Kubernetes)
- [ ] Configure monitoring and alerting
- [ ] Set up automated backups
- [ ] Implement log aggregation

## Dependencies
- All previous stories (1-5) must be completed
- Docker Desktop installed on development machines

## Notes
- Use Docker multi-stage builds for optimal image sizes
- Implement proper secret management for production
- Consider using Docker Swarm or Kubernetes for production
- Set up monitoring and logging from the start
- Regular security updates for base images
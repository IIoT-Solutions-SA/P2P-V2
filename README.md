# P2P Sandbox Platform

**A peer-driven collaboration platform for Saudi Arabia's industrial SMEs featuring forums, use case submissions, and knowledge sharing capabilities.**

## 🚀 Quick Start

Get the entire application running in 3 commands:

```bash
# Clone and enter directory
git clone <repository-url>
cd P2P-V2

# Start all services with Docker
./docker-control.sh start

# Access the application
# Frontend: http://localhost:5173
# Backend:  http://localhost:8000/docs
```

## 📋 Prerequisites

- **Docker Desktop** (required)
- **Git** (required)
- **Node.js 20+** (optional - only if running frontend locally)
- **Python 3.11+** (optional - only if running backend locally)

## 🏗️ Architecture Overview

### Tech Stack
- **Frontend**: React 19 + TypeScript + Vite + TailwindCSS + shadcn/ui
- **Backend**: FastAPI (Python) with Async/Await
- **Databases**: PostgreSQL (async with AsyncPG) + MongoDB (async with Motor)
- **Authentication**: SuperTokens
- **Caching**: Redis
- **Containerization**: Docker + Docker Compose

### Services
| Service | Port | Purpose |
|---------|------|---------|
| Frontend | 5173 | React application with hot reload |
| Backend | 8000 | FastAPI server + API documentation |
| PostgreSQL | 5432 | Relational data (users, organizations, forum topics) |
| MongoDB | 27017 | Document data (forum posts, use cases) |
| Redis | 6379 | Caching and session storage |
| SuperTokens | 3567 | Authentication service |

## 🎯 Access Points

- **Application**: http://localhost:5173
- **API Documentation**: http://localhost:8000/docs
- **API Health Check**: http://localhost:8000/health
- **Backend API**: http://localhost:8000

## 💻 Development Setup

### Option 1: Docker (Recommended)

```bash
# Start all services
./docker-control.sh start

# View logs
./docker-control.sh logs

# Stop services
./docker-control.sh stop

# Clean restart
./docker-control.sh restart
```

### Option 2: Local Development

<details>
<summary>Click to expand local setup instructions</summary>

#### Backend Setup
```bash
cd p2p-backend-app

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Start databases with Docker
docker-compose up -d postgres mongodb redis supertokens

# Run migrations
alembic upgrade head

# Start backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup
```bash
cd p2p-frontend-app

# Install dependencies
npm install

# Start frontend
npm run dev
```
</details>

## 🧪 Testing Accounts

The system comes with pre-configured test accounts:

| Email | Role | Use Case |
|-------|------|----------|
| `admin.test@company.sa` | Admin | General testing |
| `newuser.journey@testcompany.sa` | Admin | User flows |
| `admin.management@testcompany.sa` | Admin | Management features |
| `password.test@testcompany.sa` | Admin | Authentication testing |
| `session.test@testcompany.sa` | Admin | Session management |

## 📁 Project Structure

```
P2P-V2/
├── README.md                   # This file - main entry point
├── DOCKER.md                   # Docker setup guide
├── CLAUDE.md                   # AI assistant context
├── docker-compose.yml          # Docker orchestration
├── docker-control.sh           # Easy Docker management
├── .env.docker                 # Docker environment config
│
├── docs/                       # Comprehensive documentation
│   ├── architecture/          # System architecture
│   ├── aadil_docs/            # Development guides
│   ├── prd/                   # Product requirements
│   └── stories/               # User stories by epic
│
├── p2p-backend-app/           # FastAPI backend
│   ├── app/                   # Application code
│   ├── alembic/               # Database migrations
│   ├── tests/                 # Test suites
│   ├── requirements.txt       # Python dependencies
│   └── Dockerfile.dev         # Development container
│
├── p2p-frontend-app/          # React frontend
│   ├── src/                   # Source code
│   ├── public/                # Static assets
│   ├── package.json           # Node dependencies
│   └── Dockerfile.dev         # Development container
│
└── docker/                    # Docker support files
    └── scripts/               # Database initialization
```

## 🔧 Common Commands

### Docker Management
```bash
# Start development environment
./docker-control.sh start

# View service status
./docker-control.sh status

# View logs (all services)
./docker-control.sh logs

# View specific service logs
./docker-control.sh logs backend
./docker-control.sh logs frontend

# Execute commands in containers
./docker-control.sh exec backend python -m pytest
./docker-control.sh exec backend alembic upgrade head

# Rebuild services
./docker-control.sh rebuild backend
./docker-control.sh rebuild

# Clean shutdown
./docker-control.sh stop

# Complete cleanup (removes all containers/volumes)
./docker-control.sh clean
```

### Development Workflow
```bash
# Make code changes (auto-reload enabled)
# Frontend: Edit files in p2p-frontend-app/src/
# Backend:  Edit files in p2p-backend-app/app/

# Run tests
./docker-control.sh exec backend python -m pytest

# Run database migrations
./docker-control.sh exec backend alembic upgrade head

# Access database directly
docker exec -it p2p-postgres psql -U postgres -d p2p_sandbox
docker exec -it p2p-mongodb mongosh p2p_sandbox
```

## 📚 Key Features Implemented

### ✅ Authentication System (Phase 2)
- SuperTokens integration with custom signup/login
- Role-based access control (Admin/Member)
- Email verification and password reset
- Session management with refresh tokens

### ✅ User Management (Phase 3)
- User profiles with organization context
- Admin user management and invitations
- Organization settings and statistics
- File upload service with validation

### ✅ Forum System (Phase 4) 
- Topic creation with categories
- Threaded replies and nested comments
- Best answer marking system
- Like/unlike functionality
- Advanced search across topics and posts

### ✅ Use Cases Module (Phase 5)
- Rich use case submission with media
- MongoDB document storage
- Advanced filtering and search
- Location-based features
- Export functionality (JSON, CSV, Excel, PDF)

### ✅ Messaging & Dashboard (Phase 6)
- Private messaging between users
- Activity feed and trending content
- Performance monitoring and caching
- Background task processing

### 🚧 Integration Phases (Pending)
- Phase 4.5: Forum frontend integration
- Phase 5.5: Use Cases frontend integration  
- Phase 6.5: Dashboard frontend integration

## 🧪 Testing

### Backend Testing
```bash
# Run all tests
./docker-control.sh exec backend python -m pytest

# Run specific test files
./docker-control.sh exec backend python -m pytest tests/unit/
./docker-control.sh exec backend python -m pytest tests/integration/

# Run with coverage
./docker-control.sh exec backend python -m pytest --cov=app
```

### Frontend Testing
```bash
# Run frontend tests
./docker-control.sh exec frontend npm test

# Run linting
./docker-control.sh exec frontend npm run lint
```

## 🔍 API Documentation

### Automatic Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/api/v1/openapi.json

### Health Checks
- **Backend Health**: http://localhost:8000/health
- **API Health**: http://localhost:8000/api/v1/health

### Key Endpoints
- **Authentication**: `/auth/*` (SuperTokens)
- **Users**: `/api/v1/users/*`
- **Organizations**: `/api/v1/organizations/*`
- **Forum**: `/api/v1/forum/*`
- **Use Cases**: `/api/v1/use-cases/*`
- **Messaging**: `/api/v1/messages/*`
- **Dashboard**: `/api/v1/dashboard/*`

## 🐛 Troubleshooting

### Common Issues

**Services won't start**
```bash
# Check Docker is running
docker version

# Check port conflicts
lsof -i :5173 :8000 :5432

# Clean restart
./docker-control.sh clean
./docker-control.sh start
```

**Database connection issues**
```bash
# Check service health
./docker-control.sh status

# Restart databases
docker-compose restart postgres mongodb redis
```

**Hot reload not working**
```bash
# Verify polling is enabled
grep -r "usePolling" p2p-frontend-app/vite.config.ts

# Check container logs
./docker-control.sh logs frontend
```

**Permission errors on Windows/WSL**
```bash
# Fix file permissions
sudo chown -R $USER:$USER .
chmod +x docker-control.sh
```

### Getting Help

1. **Check logs**: `./docker-control.sh logs [service]`
2. **Verify services**: `./docker-control.sh status`
3. **Clean restart**: `./docker-control.sh clean && ./docker-control.sh start`
4. **Review documentation**: `/docs/` directory

## 🚀 Deployment

### Development
- Uses hot reload for both frontend and backend
- Development Dockerfiles with volume mounts
- Debug ports exposed (5678 for backend)

### Production
```bash
# Build production images
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

# Deploy to production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

See `/docs/aadil_docs/aws-deployment-cicd-plan.md` for AWS ECS deployment.

## 📈 Development Status

- **Phase 0-6**: ✅ **Complete** (All core backend features implemented)
- **Integration Phases**: 🚧 **Pending** (Frontend-backend integration)
- **Phase 7**: 🚧 **Pending** (Testing & deployment)

**Current Branch**: `aadil-backend`  
**Main Branch**: `main`

## 🤝 Contributing

1. Work on the `aadil-backend` branch
2. Follow async/await patterns for all I/O
3. Update tests for new features
4. Run `./docker-control.sh exec backend python -m pytest` before commits
5. Update this README for major changes

## 📄 License

[Add your license information here]

---

**Need help?** Check the comprehensive documentation in `/docs/` or review `DOCKER.md` for container-specific guidance.
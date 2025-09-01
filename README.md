# P2P Sandbox - Manufacturing Knowledge Platform

A comprehensive platform for manufacturing professionals to share use cases, discuss solutions, and collaborate on industrial challenges.

## 🚀 Quick Start with Docker

### Prerequisites
- Docker Desktop installed and running
- Git (to clone the repository)

### Launch the Complete Stack

1. **Navigate to the docker directory:**
   ```bash
   cd docker
   ```

2. **Start all services:**
   
   **Production Mode (Default):**
   ```bash
   docker-compose up --build
   ```
   - **Frontend:** http://15.185.167.236:5173 (accessible to everyone)
   - **Backend API:** http://15.185.167.236:8000
   - **API Documentation:** http://15.185.167.236:8000/docs
   - Uses production-optimized Docker builds
   - Minified frontend assets, optimized for deployment

   **Development Mode (Recommended for local development):**
   ```bash
   MODE=development docker-compose up --build
   ```
   - **Frontend:** http://localhost:5173 (local only)
   - **Backend API:** http://localhost:8000
   - **API Documentation:** http://localhost:8000/docs
   - Uses production Docker builds with development runtime settings
   - Hot reload enabled, source maps available, no minification

   For PowerShell:
   ```powershell
   $env:MODE="development"; docker-compose up --build
   ```

   **Note:** Both modes use production-optimized Docker images. The `MODE` variable only affects runtime behavior (hot reload, minification, API URLs). This hybrid approach ensures you develop with production-like containers while maintaining developer conveniences.

### What Gets Started
- ✅ PostgreSQL database (with SuperTokens schema)
- ✅ MongoDB database (with authentication)
- ✅ Backend API server (FastAPI)
- ✅ Frontend application (React + Vite)
- ✅ Automated database migrations
- ✅ Complete data seeding (18 demo users + sample content)

### Demo Users
The system comes pre-loaded with 18 demo users. Use the login page to access any of them with one-click authentication.

### Stop the Stack
```bash
# Stop services
docker-compose down

# Stop and remove all data (fresh start)
docker-compose down -v
```

## 🌐 Environment Configuration

### Production Mode (Default)
- **No environment variables needed**
- Uses IP address: `15.185.167.236`
- Accessible from anywhere on the internet
- Just run: `docker-compose up`
- Production-optimized builds with minified assets

### Development Mode
- For local testing and development
- Uses localhost addresses
- PowerShell: `$env:MODE="development"; docker-compose up`
- Bash: `MODE=development docker-compose up`
- Production Docker builds with development runtime (hot reload, source maps)

### IP Address Changes
If the EC2 IP address changes, update the hardcoded IP in:
`p2p-frontend-app/src/config/environment.ts`

### Troubleshooting
- Ensure Docker Desktop is running
- Check that all containers are healthy: `docker-compose ps`
- For fresh start: `docker-compose down -v`

### Development Features
- 🔥 **Hot Reloading:** Both frontend and backend update on code changes
- 📊 **Full Data:** Complete with users, forum posts, use cases, and activities
- 🔐 **Authentication:** SuperTokens integration ready to use
- 🐳 **One Command:** Entire development environment in seconds
- 🌐 **Network Ready:** Configurable for different machines and IPs

---

## Architecture
- **Frontend:** React + TypeScript + Vite + Tailwind CSS
- **Backend:** FastAPI + Python + SQLAlchemy + Beanie ODM
- **Databases:** PostgreSQL (users/auth) + MongoDB (content)
- **Authentication:** SuperTokens
- **Containerization:** Docker + Docker Compose

## Documentation
Detailed implementation stories and technical documentation available in the `backend docs/` directory.

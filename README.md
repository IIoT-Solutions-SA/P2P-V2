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
   ```bash
   docker-compose up --build
   ```

3. **Access the application:**
   - **Frontend:** http://localhost:5173
   - **Backend API:** http://localhost:8000
   - **API Documentation:** http://localhost:8000/docs

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

### Development Features
- 🔥 **Hot Reloading:** Both frontend and backend update on code changes
- 📊 **Full Data:** Complete with users, forum posts, use cases, and activities
- 🔐 **Authentication:** SuperTokens integration ready to use
- 🐳 **One Command:** Entire development environment in seconds

---

## Architecture
- **Frontend:** React + TypeScript + Vite + Tailwind CSS
- **Backend:** FastAPI + Python + SQLAlchemy + Beanie ODM
- **Databases:** PostgreSQL (users/auth) + MongoDB (content)
- **Authentication:** SuperTokens
- **Containerization:** Docker + Docker Compose

## Documentation
Detailed implementation stories and technical documentation available in the `backend docs/` directory.

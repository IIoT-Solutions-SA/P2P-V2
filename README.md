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

## 🐳 Docker Philosophy - It Just Works!

The Docker setup is designed to work out-of-the-box on any machine without configuration changes. The system automatically handles:

- ✅ **Cross-platform compatibility** (Windows, Mac, Linux)
- ✅ **Network configuration** (localhost, 127.0.0.1, container networking)
- ✅ **CORS handling** (pre-configured for common Docker scenarios)
- ✅ **Database connections** (automatic service discovery)

### Accessing from Different Machines
If you want to access the application from other machines on your network:

1. **The Docker containers will work as-is** - no code changes needed
2. **Access via your machine's IP:**
   - Find your IP: `ipconfig` (Windows) or `ifconfig` (Mac/Linux)  
   - Frontend: `http://YOUR_IP:5173`
   - Backend: `http://YOUR_IP:8000`
3. **The application will work** because CORS is pre-configured for common scenarios

### Troubleshooting
If you encounter any issues:
- Ensure Docker Desktop is running
- Try accessing via `http://localhost:5173` first
- Check that all containers are healthy: `docker-compose ps`
- **If backend fails to start**: Ensure no local `.env` files are interfering (they're excluded via .dockerignore)

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

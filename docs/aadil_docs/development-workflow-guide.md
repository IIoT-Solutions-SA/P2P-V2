# Development Workflow Guide for P2P Sandbox

## Overview
This guide establishes an efficient development workflow for the P2P Sandbox platform, covering concurrent frontend-backend development, environment management, debugging techniques, and team collaboration practices.

## Table of Contents
1. [Development Environment Setup](#development-environment-setup)
2. [Concurrent Development](#concurrent-development)
3. [Git Workflow](#git-workflow)
4. [Database Management](#database-management)
5. [Debugging Strategies](#debugging-strategies)
6. [Testing Workflow](#testing-workflow)
7. [Code Quality Standards](#code-quality-standards)
8. [Deployment Pipeline](#deployment-pipeline)
9. [Team Collaboration](#team-collaboration)
10. [Troubleshooting Guide](#troubleshooting-guide)

## Development Environment Setup

### Initial Setup Checklist

1. **Prerequisites**
   - [ ] Docker Desktop installed
   - [ ] Node.js 18+ installed
   - [ ] Python 3.11+ installed
   - [ ] Git configured
   - [ ] VS Code or preferred IDE

2. **Repository Setup**
   ```bash
   # Clone repository
   git clone <repository-url>
   cd p2p-v2
   
   # Check out development branch
   git checkout aadil-backend
   
   # Copy environment files
   cp .env.example .env
   cp p2p-frontend-app/.env.example p2p-frontend-app/.env.development
   ```

3. **Docker Environment**
   ```bash
   # Build and start all services
   docker-compose up -d
   
   # Verify all services are healthy
   docker-compose ps
   
   # Check logs if needed
   docker-compose logs -f
   ```

### Environment Configuration

1. **Backend Environment (.env)**
   ```
   # Database
   DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/p2p_sandbox
   MONGODB_URL=mongodb://localhost:27017/p2p_sandbox
   
   # SuperTokens
   SUPERTOKENS_CONNECTION_URI=http://localhost:3567
   
   # Development
   DEBUG=True
   LOG_LEVEL=DEBUG
   ```

2. **Frontend Environment (.env.development)**
   ```
   VITE_API_URL=http://localhost:8000/api/v1
   VITE_SUPERTOKENS_URL=http://localhost:3567
   VITE_WEBSOCKET_URL=ws://localhost:8000/ws
   ```

## Concurrent Development

### Running Frontend and Backend Together

1. **Option 1: Docker for Backend, Local for Frontend**
   ```bash
   # Terminal 1: Start backend services
   docker-compose up postgres mongodb redis supertokens backend
   
   # Terminal 2: Start frontend
   cd p2p-frontend-app
   npm install
   npm run dev
   ```

2. **Option 2: Everything in Docker**
   ```bash
   # Start all services including frontend
   docker-compose up
   
   # Frontend available at http://localhost:3000
   # Backend available at http://localhost:8000
   ```

3. **Option 3: Hybrid Development**
   ```bash
   # Start only databases and services
   docker-compose up postgres mongodb redis supertokens
   
   # Run backend locally
   cd p2p-backend-app
   source venv/bin/activate
   uvicorn app.main:app --reload
   
   # Run frontend locally
   cd p2p-frontend-app
   npm run dev
   ```

### Hot Reload Configuration

1. **Backend Hot Reload**
   - Automatic with `--reload` flag
   - Watches all Python files
   - Restarts on changes

2. **Frontend Hot Reload**
   - Vite provides HMR (Hot Module Replacement)
   - Instant updates without refresh
   - Preserves component state

### Network Communication

```
Frontend (localhost:5173)
    ↓
Backend API (localhost:8000)
    ↓
Databases (Docker Network)
```

## Git Workflow

### Branch Strategy

1. **Main Branches**
   - `main`: Production-ready code
   - `develop`: Integration branch
   - `aadil-backend`: Your working branch

2. **Feature Branches**
   ```bash
   # Create feature branch
   git checkout -b feature/user-authentication
   
   # Work on feature
   git add .
   git commit -m "feat: implement user login endpoint"
   
   # Push to remote
   git push origin feature/user-authentication
   ```

### Commit Conventions

1. **Commit Message Format**
   ```
   <type>(<scope>): <subject>
   
   <body>
   
   <footer>
   ```

2. **Types**
   - `feat`: New feature
   - `fix`: Bug fix
   - `docs`: Documentation
   - `style`: Code style
   - `refactor`: Code refactoring
   - `test`: Testing
   - `chore`: Maintenance

3. **Examples**
   ```bash
   git commit -m "feat(auth): add SuperTokens integration"
   git commit -m "fix(api): resolve CORS issue with credentials"
   git commit -m "docs(readme): update setup instructions"
   ```

### Pull Request Process

1. **Before Creating PR**
   - [ ] All tests pass
   - [ ] Code formatted
   - [ ] Documentation updated
   - [ ] No merge conflicts

2. **PR Template**
   ```markdown
   ## Description
   Brief description of changes
   
   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change
   
   ## Testing
   - [ ] Unit tests pass
   - [ ] Integration tests pass
   - [ ] Manual testing completed
   
   ## Checklist
   - [ ] Code follows style guidelines
   - [ ] Self-review completed
   - [ ] Documentation updated
   ```

## Database Management

### Migration Workflow

1. **Creating Migrations**
   ```bash
   # Generate migration from model changes
   docker-compose exec backend alembic revision --autogenerate -m "Add user table"
   
   # Create empty migration
   docker-compose exec backend alembic revision -m "Custom migration"
   ```

2. **Applying Migrations**
   ```bash
   # Apply all migrations
   docker-compose exec backend alembic upgrade head
   
   # Rollback one migration
   docker-compose exec backend alembic downgrade -1
   
   # View migration history
   docker-compose exec backend alembic history
   ```

### Database Access

1. **PostgreSQL Access**
   ```bash
   # Connect via docker
   docker-compose exec postgres psql -U postgres -d p2p_sandbox
   
   # Connect locally
   psql -h localhost -U postgres -d p2p_sandbox
   ```

2. **MongoDB Access**
   ```bash
   # Connect via docker
   docker-compose exec mongodb mongosh p2p_sandbox
   
   # Connect locally
   mongosh mongodb://localhost:27017/p2p_sandbox
   ```

### Data Management

1. **Backup**
   ```bash
   # PostgreSQL backup
   docker-compose exec postgres pg_dump -U postgres p2p_sandbox > backup.sql
   
   # MongoDB backup
   docker-compose exec mongodb mongodump --db p2p_sandbox --out /backup
   ```

2. **Restore**
   ```bash
   # PostgreSQL restore
   docker-compose exec -T postgres psql -U postgres p2p_sandbox < backup.sql
   
   # MongoDB restore
   docker-compose exec mongodb mongorestore --db p2p_sandbox /backup/p2p_sandbox
   ```

## Debugging Strategies

### Backend Debugging

1. **VS Code Configuration**
   ```json
   {
     "name": "Python: Remote Attach",
     "type": "python",
     "request": "attach",
     "connect": {
       "host": "localhost",
       "port": 5678
     },
     "pathMappings": [{
       "localRoot": "${workspaceFolder}/p2p-backend-app",
       "remoteRoot": "/app"
     }]
   }
   ```

2. **Debug Mode**
   ```bash
   # Start backend with debugger
   docker-compose run -p 5678:5678 backend \
     python -m debugpy --listen 0.0.0.0:5678 \
     -m uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

3. **Logging**
   ```python
   import logging
   logger = logging.getLogger(__name__)
   
   # Use throughout code
   logger.debug("Debug information")
   logger.info("General information")
   logger.error("Error occurred", exc_info=True)
   ```

### Frontend Debugging

1. **Browser DevTools**
   - React Developer Tools
   - Network tab for API calls
   - Console for errors
   - Sources for breakpoints

2. **VS Code Debugging**
   ```json
   {
     "type": "chrome",
     "request": "launch",
     "name": "Launch Chrome",
     "url": "http://localhost:5173",
     "webRoot": "${workspaceFolder}/p2p-frontend-app"
   }
   ```

3. **Debug Utilities**
   ```typescript
   // Debug logging
   if (import.meta.env.DEV) {
     console.log('Debug:', data);
   }
   
   // React Query DevTools
   import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
   ```

## Testing Workflow

### Running Tests

1. **Backend Tests**
   ```bash
   # Run all tests
   docker-compose exec backend pytest
   
   # Run specific test file
   docker-compose exec backend pytest tests/test_auth.py
   
   # Run with coverage
   docker-compose exec backend pytest --cov=app
   
   # Run in watch mode
   docker-compose exec backend ptw
   ```

2. **Frontend Tests**
   ```bash
   # Run tests
   cd p2p-frontend-app
   npm test
   
   # Run with coverage
   npm run test:coverage
   
   # Run in watch mode
   npm run test:watch
   ```

### Test-Driven Development

1. **Workflow**
   ```
   1. Write failing test
   2. Write minimal code to pass
   3. Refactor
   4. Repeat
   ```

2. **Example Flow**
   ```bash
   # 1. Create test
   # 2. Run test (should fail)
   docker-compose exec backend pytest tests/test_new_feature.py
   # 3. Implement feature
   # 4. Run test (should pass)
   # 5. Refactor if needed
   ```

## Code Quality Standards

### Automated Formatting

1. **Backend (Python)**
   ```bash
   # Format with Black
   docker-compose exec backend black .
   
   # Sort imports
   docker-compose exec backend isort .
   
   # Type checking
   docker-compose exec backend mypy .
   ```

2. **Frontend (TypeScript)**
   ```bash
   # Format with Prettier
   cd p2p-frontend-app
   npm run format
   
   # Lint with ESLint
   npm run lint
   
   # Type checking
   npm run type-check
   ```

### Pre-commit Hooks

1. **Setup**
   ```bash
   # Install pre-commit
   pip install pre-commit
   
   # Install hooks
   pre-commit install
   ```

2. **Configuration (.pre-commit-config.yaml)**
   ```yaml
   repos:
     - repo: https://github.com/psf/black
       rev: 23.0.0
       hooks:
         - id: black
     - repo: https://github.com/pycqa/isort
       rev: 5.12.0
       hooks:
         - id: isort
   ```

## Deployment Pipeline

### Development Deployment

1. **Build Images**
   ```bash
   # Build development images
   docker-compose build
   
   # Push to registry
   docker-compose push
   ```

2. **Deploy to Development**
   ```bash
   # Deploy stack
   docker stack deploy -c docker-compose.yml p2p-dev
   
   # Check status
   docker service ls
   ```

### Production Preparation

1. **Build Production Images**
   ```bash
   # Build with production Dockerfile
   docker build -f Dockerfile.prod -t p2p-backend:latest .
   ```

2. **Environment Variables**
   - Use secrets management
   - Different database credentials
   - Production URLs
   - Disable debug mode

## Team Collaboration

### Code Review Guidelines

1. **What to Review**
   - Code correctness
   - Performance implications
   - Security concerns
   - Documentation completeness
   - Test coverage

2. **Review Checklist**
   - [ ] Code follows conventions
   - [ ] No obvious bugs
   - [ ] Adequate error handling
   - [ ] Performance acceptable
   - [ ] Security considered

### Documentation Standards

1. **Code Documentation**
   - Docstrings for functions
   - Comments for complex logic
   - Type hints everywhere
   - README updates

2. **API Documentation**
   - OpenAPI specs updated
   - Example requests/responses
   - Error scenarios documented
   - Authentication requirements

### Communication Channels

1. **Development Updates**
   - Daily standup notes
   - PR descriptions
   - Commit messages
   - Issue tracking

2. **Knowledge Sharing**
   - Technical decisions documented
   - Architecture diagrams updated
   - Lessons learned recorded
   - Best practices shared

## Troubleshooting Guide

### Common Issues

1. **Container Won't Start**
   ```bash
   # Check logs
   docker-compose logs backend
   
   # Rebuild image
   docker-compose build --no-cache backend
   
   # Remove volumes and restart
   docker-compose down -v
   docker-compose up
   ```

2. **Database Connection Failed**
   ```bash
   # Check if database is running
   docker-compose ps postgres
   
   # Test connection
   docker-compose exec postgres pg_isready
   
   # Check environment variables
   docker-compose exec backend env | grep DATABASE
   ```

3. **Frontend Can't Reach Backend**
   - Check CORS configuration
   - Verify API URL in environment
   - Check if backend is running
   - Inspect network requests

4. **Hot Reload Not Working**
   - Check volume mounts
   - Verify file watchers
   - Restart containers
   - Check file permissions

### Debug Commands

```bash
# View running containers
docker ps

# Inspect container
docker inspect p2p-backend

# View container logs
docker logs -f p2p-backend

# Execute commands in container
docker exec -it p2p-backend bash

# Check resource usage
docker stats

# Clean up everything
docker system prune -a
```

## Daily Workflow Summary

1. **Morning**
   ```bash
   # Update code
   git pull origin aadil-backend
   
   # Start services
   docker-compose up -d
   
   # Check service health
   docker-compose ps
   ```

2. **During Development**
   - Write tests first
   - Implement features
   - Run tests frequently
   - Commit often

3. **Before Break**
   ```bash
   # Run all tests
   docker-compose exec backend pytest
   
   # Format code
   docker-compose exec backend black .
   
   # Commit changes
   git add .
   git commit -m "feat: description"
   git push
   ```

4. **End of Day**
   ```bash
   # Stop services (optional)
   docker-compose down
   
   # Document any issues
   # Update task tracking
   ```
# Contributing to P2P Sandbox

## Getting Started

1. **Setup Development Environment**
   ```bash
   git clone <repository-url>
   cd P2P-V2
   ./docker-control.sh start
   ```

2. **Verify Setup**
   - Frontend: http://localhost:5173
   - Backend: http://localhost:8000/docs
   - All tests pass: `./docker-control.sh exec backend python -m pytest`

## Development Workflow

### Branch Strategy
- **Main branch**: `main` (production-ready code)
- **Development branch**: `aadil-backend` (active development)
- Work on feature branches from `aadil-backend`

### Making Changes

1. **Start Development Environment**
   ```bash
   ./docker-control.sh start
   ```

2. **Make Your Changes**
   - Frontend: Edit files in `p2p-frontend-app/src/`
   - Backend: Edit files in `p2p-backend-app/app/`
   - Hot reload is enabled for both

3. **Test Your Changes**
   ```bash
   # Run backend tests
   ./docker-control.sh exec backend python -m pytest
   
   # Run frontend tests
   ./docker-control.sh exec frontend npm test
   
   # Test API endpoints
   curl http://localhost:8000/health
   ```

4. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

### Code Standards

#### Backend (Python/FastAPI)
- Use **async/await** for all I/O operations
- Follow existing patterns in `/app` directory
- Add type hints for all functions
- Write tests for new endpoints
- Use Pydantic schemas for request/response validation

#### Frontend (React/TypeScript)
- Use TypeScript for all new components
- Follow existing component structure in `/src`
- Use TailwindCSS for styling
- Update types in `/src/types` when needed

#### Database
- Create Alembic migrations for schema changes
- Use async database sessions
- Follow existing model patterns

### Testing

#### Required Tests
- **Backend**: Unit tests for new functions/endpoints
- **Integration**: Test database operations
- **API**: Test all new endpoints

#### Running Tests
```bash
# All backend tests
./docker-control.sh exec backend python -m pytest

# Specific test file
./docker-control.sh exec backend python -m pytest tests/unit/test_auth.py

# With coverage
./docker-control.sh exec backend python -m pytest --cov=app

# Frontend tests
./docker-control.sh exec frontend npm test
```

## Code Review Process

1. **Before Submitting**
   - [ ] All tests pass
   - [ ] No linting errors
   - [ ] API documentation updated (if needed)
   - [ ] README updated (if needed)

2. **Commit Message Format**
   ```
   type: brief description
   
   Longer description of what was changed and why.
   ```
   
   Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

## Common Tasks

### Adding a New API Endpoint
1. Create route in `/app/api/v1/`
2. Add Pydantic schemas in `/app/schemas/`
3. Implement business logic in `/app/services/`
4. Add database operations in `/app/crud/`
5. Write tests in `/tests/`
6. Test with frontend integration

### Adding a New React Component
1. Create component in `/src/components/`
2. Add types in `/src/types/`
3. Update routing if needed
4. Add to existing pages/layouts
5. Test in browser

### Database Changes
1. Update models in `/app/models/`
2. Create migration: `./docker-control.sh exec backend alembic revision --autogenerate -m "description"`
3. Apply migration: `./docker-control.sh exec backend alembic upgrade head`
4. Update CRUD operations and schemas

## Debugging

### Backend Debugging
```bash
# View logs
./docker-control.sh logs backend

# Debug in container
./docker-control.sh exec backend python -c "import app.main; print('Backend loaded')"

# Database inspection
docker exec p2p-postgres psql -U postgres -d p2p_sandbox
```

### Frontend Debugging
```bash
# View logs  
./docker-control.sh logs frontend

# Check build
./docker-control.sh exec frontend npm run build
```

## Environment Setup

### Environment Variables
- Copy `.env.example` to `.env.docker`
- Customize values as needed for local development
- Never commit secrets or passwords

### External Services
- SuperTokens: Automatically configured
- Databases: Automatically initialized
- All services start with `./docker-control.sh start`

## Performance Considerations

- Use async/await for all database operations
- Implement pagination for large data sets
- Use caching (Redis) for frequently accessed data
- Optimize database queries with proper indexes

## Security Guidelines

- Never hardcode secrets in source code
- Use environment variables for sensitive data
- Validate all user inputs with Pydantic
- Use RBAC for permission checking
- Follow OWASP security guidelines

## Documentation

### Required Documentation Updates
- Update README.md for major features
- Update API documentation (auto-generated from code)
- Update DOCKER.md for deployment changes
- Add comments for complex business logic

### Architecture Documentation
- System changes: Update `/docs/architecture/`
- New features: Update `/docs/stories/`
- Development guides: Update `/docs/aadil_docs/`

## Need Help?

1. **Check Documentation**: `/docs/` directory
2. **Review Examples**: Existing similar code
3. **Test Setup**: Run `./docker-control.sh status`
4. **Clean Restart**: `./docker-control.sh clean && ./docker-control.sh start`

## Release Process

1. All features implemented and tested
2. Documentation updated
3. Tests passing
4. Merge to `main` branch
5. Deploy to production with `docker-compose.prod.yml`
# P2P Sandbox Backend

FastAPI backend for the P2P Sandbox platform - a peer-driven collaboration platform for Saudi Arabia's industrial SMEs.

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.11+ (for local development)
- Git

### Getting Started

1. **Clone and setup environment**
   ```bash
   cd p2p-backend-app
   cp .env.example .env
   # Edit .env with your configuration
   ```

2. **Start all services with Docker**
   ```bash
   docker-compose up
   ```

3. **Run database migrations**
   ```bash
   docker-compose exec backend alembic upgrade head
   ```

4. **Access the application**
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Frontend: http://localhost:5173

## Development

### Container Services
- **Backend**: FastAPI application (port 8000)
- **PostgreSQL**: Primary database (port 5432)
- **MongoDB**: Document storage (port 27017)
- **Redis**: Caching and sessions (port 6379)
- **SuperTokens**: Authentication service (port 3567)

### Common Commands

```bash
# Start services
docker-compose up

# Run tests
docker-compose exec backend pytest

# Create new migration
docker-compose exec backend alembic revision --autogenerate -m "Description"

# Format code
docker-compose exec backend black .
docker-compose exec backend ruff . --fix

# Type checking
docker-compose exec backend mypy .

# Security scan
~/.local/bin/semgrep --config=auto .
```

### Project Structure

```
p2p-backend-app/
├── app/
│   ├── api/           # API endpoints
│   ├── core/          # Core functionality
│   ├── db/            # Database configuration
│   ├── models/        # SQLModel definitions
│   ├── schemas/       # Pydantic schemas
│   ├── services/      # Business logic
│   └── main.py        # Application entry
├── tests/             # Test suite
├── alembic/           # Database migrations
├── scripts/           # Utility scripts
└── docker-compose.yml # Container orchestration
```

## API Documentation

Once the application is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Testing

```bash
# Run all tests
docker-compose exec backend pytest

# Run with coverage
docker-compose exec backend pytest --cov=app --cov-report=html

# Run specific test
docker-compose exec backend pytest tests/test_auth.py -v
```

## Contributing

1. Always work on the `aadil-backend` branch
2. Write tests for new features
3. Ensure all tests pass before committing
4. Use conventional commit messages
5. Run security scans on new code

## Documentation

- [Backend Development Plan](../docs/aadil_docs/unified-backend-development-plan.md)
- [Implementation Tasks](../docs/aadil_docs/backend-implementation-tasks.md)
- [API Communication Guide](../docs/aadil_docs/api-communication-guide.md)
- [Development Workflow](../docs/aadil_docs/development-workflow-guide.md)

## License

[License information here]
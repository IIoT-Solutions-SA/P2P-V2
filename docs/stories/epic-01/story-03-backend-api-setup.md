# Story 3: Backend API Framework Setup

## Story Details
**Epic**: Epic 1 - Project Foundation & Development Environment  
**Story Points**: 5  
**Priority**: High  
**Dependencies**: Story 1 (Repository Initialization)

## User Story
**As a** backend developer  
**I want** a configured FastAPI environment with proper structure  
**So that** I can start building API endpoints efficiently

## Acceptance Criteria
- [ ] Python virtual environment configured with all dependencies
- [ ] FastAPI application with modular structure
- [ ] CORS properly configured for frontend communication
- [ ] Health check and info endpoints implemented
- [ ] OpenAPI/Swagger documentation auto-generated and accessible
- [ ] Structured logging configured with appropriate levels
- [ ] Environment-based configuration management
- [ ] Basic error handling and validation
- [ ] API versioning structure in place

## Technical Specifications

### 1. Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── core/               # Core functionality
│   │   ├── __init__.py
│   │   ├── config.py       # Configuration management
│   │   ├── security.py     # Security utilities
│   │   └── logging.py      # Logging configuration
│   ├── api/                # API endpoints
│   │   ├── __init__.py
│   │   ├── deps.py         # Common dependencies
│   │   └── v1/             # API version 1
│   │       ├── __init__.py
│   │       ├── api.py      # API router aggregation
│   │       └── endpoints/  # Individual endpoints
│   │           ├── __init__.py
│   │           ├── health.py
│   │           └── info.py
│   ├── models/             # Pydantic models
│   │   ├── __init__.py
│   │   └── common.py
│   ├── schemas/            # API schemas
│   │   ├── __init__.py
│   │   └── common.py
│   ├── services/           # Business logic
│   │   └── __init__.py
│   └── utils/              # Utility functions
│       ├── __init__.py
│       └── validators.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── api/
│       └── test_health.py
├── alembic/                # Database migrations (created in Story 4)
├── requirements.txt
├── requirements-dev.txt
├── .env.example
├── pytest.ini
└── pyproject.toml
```

### 2. Dependencies

#### requirements.txt
```
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-dotenv==1.0.0
pydantic==2.5.0
pydantic-settings==2.1.0
python-multipart==0.0.6
email-validator==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
tenacity==8.2.3
httpx==0.26.0
```

#### requirements-dev.txt
```
-r requirements.txt
pytest==7.4.4
pytest-asyncio==0.23.3
pytest-cov==4.1.0
black==23.12.1
isort==5.13.2
flake8==7.0.0
mypy==1.8.0
pre-commit==3.6.0
```

### 3. Core Configuration

#### app/core/config.py
```python
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, validator
import secrets

class Settings(BaseSettings):
    # API Settings
    API_TITLE: str = "P2P Sandbox API"
    API_VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "P2P Sandbox for SMEs"
    
    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Database (will be used in Story 4)
    DATABASE_URL: Optional[str] = None
    MONGODB_URL: Optional[str] = None
    
    # SuperTokens (will be used in Story 5)
    SUPERTOKENS_CONNECTION_URI: Optional[str] = None
    SUPERTOKENS_API_KEY: Optional[str] = None
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
```

#### app/core/logging.py
```python
import logging
import sys
from pathlib import Path
from loguru import logger
from app.core.config import settings

class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )

def setup_logging():
    # Remove default logger
    logger.remove()
    
    # Console logging
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="DEBUG" if settings.DEBUG else "INFO",
        backtrace=True,
        diagnose=True,
    )
    
    # File logging
    logger.add(
        "logs/p2p-sandbox.log",
        rotation="500 MB",
        retention="10 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="INFO",
        backtrace=True,
        diagnose=True,
    )
    
    # Intercept standard logging
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    
    # Set specific log levels for libraries
    for logger_name in ["uvicorn", "uvicorn.access", "fastapi"]:
        logging.getLogger(logger_name).handlers = [InterceptHandler()]
        
    return logger
```

### 4. Main Application

#### app/main.py
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.logging import setup_logging
from app.api.v1.api import api_router

# Setup logging
logger = setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info(f"Starting {settings.PROJECT_NAME}")
    yield
    # Shutdown
    logger.info("Shutting down")

app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# CORS middleware
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include routers
app.include_router(api_router, prefix=settings.API_V1_STR)

# Root endpoint
@app.get("/")
async def root():
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.API_VERSION,
        "environment": settings.ENVIRONMENT
    }
```

### 5. API Endpoints

#### app/api/v1/api.py
```python
from fastapi import APIRouter
from app.api.v1.endpoints import health, info

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(info.router, prefix="/info", tags=["info"])
```

#### app/api/v1/endpoints/health.py
```python
from fastapi import APIRouter, status
from datetime import datetime
from app.schemas.common import HealthResponse
import psutil
import platform

router = APIRouter()

@router.get("/", response_model=HealthResponse)
async def health_check():
    """Check the health status of the API"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version="1.0.0",
        uptime=psutil.boot_time(),
        checks={
            "api": "ok",
            "database": "pending",  # Will be implemented in Story 4
            "cache": "pending"      # Future implementation
        }
    )

@router.get("/ready")
async def readiness_check():
    """Check if the service is ready to accept requests"""
    # Add readiness checks here (DB connections, etc.)
    return {"ready": True}

@router.get("/live")
async def liveness_check():
    """Check if the service is alive"""
    return {"alive": True}
```

#### app/api/v1/endpoints/info.py
```python
from fastapi import APIRouter
from app.core.config import settings
import platform
import sys

router = APIRouter()

@router.get("/")
async def get_api_info():
    """Get information about the API"""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.API_VERSION,
        "environment": settings.ENVIRONMENT,
        "python_version": sys.version,
        "platform": platform.platform(),
        "docs_url": f"{settings.API_V1_STR}/docs",
        "openapi_url": f"{settings.API_V1_STR}/openapi.json"
    }

@router.get("/status")
async def get_status():
    """Get current system status"""
    return {
        "status": "operational",
        "services": {
            "api": "running",
            "database": "not_configured",
            "authentication": "not_configured"
        }
    }
```

### 6. Schemas

#### app/schemas/common.py
```python
from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Any

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str
    uptime: float
    checks: Dict[str, str]

class ErrorResponse(BaseModel):
    error: str
    message: str
    timestamp: datetime
    path: str
    
class SuccessResponse(BaseModel):
    success: bool
    message: str
    data: Any = None
```

### 7. Testing Setup

#### pytest.ini
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --cov=app --cov-report=term-missing --cov-report=html
asyncio_mode = auto
```

#### tests/conftest.py
```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
def async_client():
    from httpx import AsyncClient
    async def _async_client():
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac
    return _async_client
```

#### tests/api/test_health.py
```python
import pytest

def test_health_check(client):
    response = client.get("/api/v1/health/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "version" in data

def test_readiness_check(client):
    response = client.get("/api/v1/health/ready")
    assert response.status_code == 200
    assert response.json()["ready"] is True

def test_liveness_check(client):
    response = client.get("/api/v1/health/live")
    assert response.status_code == 200
    assert response.json()["alive"] is True
```

### 8. Development Scripts

#### backend/scripts/dev.sh
```bash
#!/bin/bash
# Development server with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### backend/scripts/test.sh
```bash
#!/bin/bash
# Run tests with coverage
pytest --cov=app --cov-report=term-missing --cov-report=html
```

## Implementation Steps

1. **Setup Python Environment**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements-dev.txt
   ```

2. **Create Application Structure**
   ```bash
   mkdir -p app/core app/api/v1/endpoints app/models app/schemas app/services app/utils
   touch app/__init__.py app/main.py
   # Create all other files as specified
   ```

3. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with development values
   ```

4. **Run Development Server**
   ```bash
   uvicorn app.main:app --reload
   ```

5. **Verify Setup**
   - Visit http://localhost:8000/docs for Swagger UI
   - Check health endpoint: http://localhost:8000/api/v1/health/
   - Run tests: `pytest`

## Testing Checklist
- [ ] API starts without errors
- [ ] Swagger documentation accessible at /docs
- [ ] Health check endpoints return correct status
- [ ] CORS headers present in responses
- [ ] Logging outputs to console and file
- [ ] Environment variables load correctly
- [ ] All tests pass

## Dependencies
- Story 1 must be completed (repository structure)
- Python 3.11+ must be installed

## Notes
- Use virtual environment for all Python development
- Keep requirements.txt updated when adding packages
- Follow PEP 8 style guidelines
- Add comprehensive docstrings to all functions